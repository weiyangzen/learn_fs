# Research: subset-b-005000

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware.h -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware.h

Purpose: This header is the shared contract for Synopsys DesignWare PCIe root-complex and endpoint glue drivers. It centralizes DWC register offsets and bit definitions, core-version/capability helpers, host and endpoint state structures, callback tables, inline DBI/config-space helpers, and exported functions implemented by the DWC core.

Important APIs, types, and functions: Version constants and helpers include `DW_PCIE_VER_*`, `dw_pcie_ver_is()`, `dw_pcie_ver_is_ge()`, and capability helpers for `REQ_RES`, `IATU_UNROLL`, and `CDM_CHECK`. Key register groups cover Port Logic link control/debug, MSI registers, Gen3 equalization, coherency control, iATU viewport/unroll programming, DBI read-only write enable, eDMA registers, RAS-DES counters, PTM, and Gen4 lane margining. Core types are `struct dw_pcie`, `struct dw_pcie_rp`, `struct dw_pcie_ep`, `struct dw_pcie_ob_atu_cfg`, `struct dw_pcie_host_ops`, `struct dw_pcie_ep_ops`, `struct dw_pcie_ep_func`, `struct dw_pcie_ops`, and `enum dw_pcie_ltssm`. Exported entry points include resource discovery, version/capability discovery, DBI access, link wait/start/stop, iATU programming, setup, eDMA detect/remove, host init/deinit/MSI setup, endpoint init/deinit/IRQ raising, and debugfs hooks.

Control flow: Platform drivers populate `struct dw_pcie`, attach vendor callbacks in `dw_pcie_ops`, then call either `dw_pcie_host_init()` through `struct dw_pcie_rp` or `dw_pcie_ep_init()` through `struct dw_pcie_ep`. The DWC core calls vendor host callbacks such as `init`, `deinit`, `post_init`, `msi_init`, and `pme_turn_off`, and calls generic vendor callbacks such as `start_link`, `stop_link`, `link_up`, `get_ltssm`, and optional DBI overrides. Inline DBI helpers funnel byte/word/dword accesses through `dw_pcie_read_dbi()`, `dw_pcie_write_dbi()`, or endpoint function-offset variants. If a vendor does not provide a callback, default wrappers either return success/no-op or use standard DWC registers such as `PCIE_PORT_DEBUG0`.

State and persistence behavior: All state is volatile kernel driver state. `struct dw_pcie` stores mapped DBI/ATU/ELBI bases, physical resource metadata, iATU window counts/limits, DesignWare version/type, link lane/speed settings, N_FTS overrides, eDMA state, clock/reset arrays, PERST GPIO, debugfs/PTM pointers, endpoint/root-port substructures, suspend state, and device mode. Root-port state tracks configuration windows, MSI domains and bitmaps, bridge pointers, ECAM/native-ECAM flags, and L2/L3 handling. Endpoint state tracks EPC, functions, inbound/outbound window bitmaps, MSI outbound iATU mapping, BAR-to-iATU assignment, and function DBI offsets. No durable storage is performed.

Dependencies and integration points: This header binds many Linux subsystems: PCI core, PCI ECAM, MSI/IRQ domains, PCI endpoint controller/function APIs, clocks, resets, GPIOs, DMA/eDMA, debugfs, PTM, and local `../../pci.h`. Vendor drivers in this directory include it to reuse the DWC core and expose their SoC-specific resource sequencing through callback tables. Conditional stubs keep glue drivers buildable when host, endpoint, or debugfs support is disabled.

Risks: This is a high-blast-radius ABI-like header inside the kernel tree. Register offsets and bitfields are hardware contracts; mistakes break many SoC drivers. Inline DBI wrappers must preserve size and function-offset behavior, especially for endpoint multi-function support. Changing structure fields or callback semantics can break platform drivers compiled in different Kconfig combinations. Read-only DBI write enable/disable sequencing is safety-critical when modifying PCI capabilities. iATU, eDMA, MSI, L1SS, and suspend fields are shared by multiple core files, so state ownership must remain clear.

Test signals: Build host-only, endpoint-only, and combined DWC configurations with a representative set of platform drivers. Exercise DBI reads/writes of all sizes, DBI2 writes, endpoint function offsets, iATU inbound/outbound programming, MSI allocation/free/dispatch, link bring-up/wait/failure, L1SS hiding, eDMA detection/removal, suspend/resume noirq paths, debugfs/PTM creation, and Kconfig-disabled stub behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-dw-rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-dw-rockchip.c

Purpose: This is the Rockchip DesignWare PCIe glue driver for RK3568 root-complex mode and RK3568/RK3588 endpoint mode. It handles Rockchip APB/client registers, clocks, reset lines, PHY, optional regulator, legacy INTx domain, LTSSM control and tracing, ASPM capability adjustments, endpoint feature reporting, and endpoint system events.

Important APIs, types, and functions: `struct rockchip_pcie` embeds `struct dw_pcie` and stores APB base, PHY, clocks, reset GPIO/control, IRQ domain, OF data, `supports_clkreq`, and delayed tracing work. `struct rockchip_pcie_of_data` selects RC or EP mode and endpoint features. Core callbacks are `rockchip_pcie_link_up()`, `rockchip_pcie_start_link()`, `rockchip_pcie_stop_link()`, and `rockchip_pcie_get_ltssm()`. Host callbacks use `rockchip_pcie_host_init()` and the INTx helpers. Endpoint callbacks include `rockchip_pcie_ep_init()`, `rockchip_pcie_raise_irq()`, `rockchip_pcie_get_features()`, and `rockchip_pcie_ep_sys_irq_thread()`.

Control flow: Probe reads match data, allocates the controller, sets default N_FTS values to 255, maps APB, gets reset GPIO/reset controls, enables optional `vpcie3v3`, initializes and powers on the PHY, deasserts controller resets, enables all clocks, then branches by mode. RC mode enables enhanced LTSSM control, writes client mode RC, initializes DWC host, sets up INTx chained IRQ, configures L1SS/CLKREQ and L0s, and clears bogus Root Port BAR0/BAR1 sizes through DBI2. EP mode requests the system IRQ, enables delayed link training for hot reset/link-down reset, writes client mode EP, initializes the DWC endpoint and registers, notifies EPC, and unmasks DLL/link-reset events. Link start asserts endpoint reset GPIO low, enables LTSSM, waits the PCIe PERST interval, starts optional tracing, then releases reset GPIO.

State and persistence behavior: State is in-memory and hardware-register state only. APB registers track mode, LTSSM enable, interrupt masks, CLKREQ/L1SS policy, LTSSM trace FIFO, and hot-reset behavior. Endpoint state is delegated to DWC EPC structures. Tracing state is a delayed work item that periodically drains the hardware LTSSM history FIFO when tracing is enabled. There is no remove callback in this file; devm resources cover allocation, but clocks/PHY are only explicitly unwound on probe failure.

Dependencies and integration points: Depends on DWC host/endpoint core, Linux PHY, regulator, clocks, reset, GPIO, IRQ domain/chained IRQ APIs, OF match data, tracepoint `pci_controller:pcie_ltssm_state_transition`, and Rockchip APB client registers. It uses DWC helpers to edit PCIe capabilities, raise endpoint INTx/MSI/MSI-X interrupts, and remove broken endpoint capabilities.

Risks: Mode sequencing is hardware-sensitive: reset assertion, regulator-before-PHY, PHY-before-reset-deassert, and clocks-before-DWC init are ordered deliberately. The INTx handler reads legacy status but does not explicitly clear it, so hardware masking/ack behavior must match expectations. The tracing work reschedules every five seconds and must be cancelled when LTSSM tracing stops. RK3588 endpoint quirks are important: ATS is hidden because ATS invalidations do not complete, and BAR4 is reserved because it exposes ATU port logic to the host. CLKREQ/L1SS policy depends on correct DT `supports-clkreq` wiring.

Test signals: Build RC and EP Kconfig variants. On RK3568 RC, verify link training, INTx domain mapping, MSI, L0s/L1SS advertisement with and without `supports-clkreq`, Root Port BAR sizing, and tracepoint output. On RK3568/RK3588 EP, verify EP init/registers, linkup/linkdown notifications on system IRQ, hot-reset delayed training, INTx/MSI/MSI-X raising, ATS capability hiding on RK3588, BAR4 reserved behavior, and cleanup paths on PHY/clock/reset probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-dw-rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-eswin.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-eswin.c

Purpose: This is the ESWIN EIC7700 DesignWare PCIe root-complex glue driver. It sequences ESWIN ELBI registers, PWR/DBI resets, per-root-port PERST resets, clocks, runtime PM, link start/link-up detection, vendor/device ID override, and PME turn-off policy for hardware that cannot enter L2/L3 Ready.

Important APIs, types, and functions: `struct eswin_pcie` embeds `struct dw_pcie`, clock bulk data, two reset controls (`pwr`, `dbi`), a list of parsed ports, and SoC data. `struct eswin_pcie_port` stores a per-port PERST reset and lane count. DWC callbacks are `eswin_pcie_start_link()` and `eswin_pcie_link_up()`. Host callbacks are `eswin_pcie_host_init()`, `eswin_pcie_host_deinit()`, and `eswin_pcie_pme_turn_off()`. Probe and PM entry points are `eswin_pcie_probe()`, `eswin_pcie_suspend_noirq()`, and `eswin_pcie_resume_noirq()`.

Control flow: Probe obtains SoC data, allocates the controller, fetches all clocks and the two named resets, parses child Root Port nodes for PERST reset and optional `num-lanes`, enables runtime PM, then calls `dw_pcie_host_init()`. The host init callback enables clocks, deasserts PWR/DBI resets, sets the DWC device type to Root Port in ELBI, cycles each child PERST reset, releases `APP_HOLD_PHY_RST`, polls `PM_SEL_AUX_CLK` until the PHY clock switch is ready, and writes ESWIN VID/DID into DBI with DBI read-only writes enabled. Link start simply sets the ELBI LTSSM enable bit; link-up reads the PCI Express Link Status DLL Link Active bit.

State and persistence behavior: Persistent effects are limited to hardware register programming while the device is active. In-memory state tracks clock count, reset descriptors, port list, lane count, and SoC data. Runtime PM keeps the device active after successful probe. `skip_l23_ready` is set during PME turn-off based on SoC data so the common DWC host code skips waiting for an unsupported L2/L3 Ready handshake.

Dependencies and integration points: Integrates with the DWC host core, runtime PM, reset framework, clock bulk APIs, OF child parsing, PCI capability/DBI helpers, and ESWIN-specific ELBI registers. The driver is built in and matches `eswin,eic7700-pcie`.

Risks: The error path in `eswin_pcie_host_init()` drops/reset-controls and list entries after failures; incorrect reuse after partial init would be risky. PERST must be deasserted before PHY configuration as described in comments. The PM_SEL_AUX_CLK poll is the main readiness gate; timeout indicates invalid PHY/clock sequencing. The driver writes vendor/device IDs over invalid defaults, so DBI read-only write bracketing must remain correct. L2/L3 behavior is intentionally skipped for EIC7700.

Test signals: Verify EIC7700 probe with child Root Port reset nodes, `num-lanes` parsing, clock/reset enable sequencing, VID/DID override visible in config space, link training, suspend/resume noirq through DWC helpers, PME turn-off without L2/L3 Ready wait, and failure injection for missing clocks/resets/PERST and PM_SEL_AUX_CLK timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-eswin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-fu740.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-fu740.c

Purpose: This is the SiFive FU740 DesignWare PCIe root-complex integration driver. It drives FU740 management registers, external PERST and power-enable GPIOs, an auxiliary clock, controller reset, PHY CR parameter programming, RC mode selection, link startup, and reboot shutdown reset.

Important APIs, types, and functions: `struct fu740_pcie` embeds `struct dw_pcie` and stores management register base, reset and power GPIOs, `pcie_aux` clock, and reset control. Hardware helpers include `fu740_pcie_assert_reset()`, `fu740_pcie_deassert_reset()`, `fu740_pcie_power_on()`, `fu740_pcie_drive_reset()`, `fu740_phyregwrite()`, and `fu740_pcie_init_phy()`. DWC callbacks are `fu740_pcie_host_init()` through `dw_pcie_host_ops` and `fu740_pcie_start_link()` through `dw_pcie_ops`.

Control flow: Probe allocates the wrapper, sets DWC ops, sets `pp.num_vectors` to `MAX_MSI_IRQS`, maps the `mgmt` region, obtains optional reset/power GPIOs, fetches `pcie_aux`, obtains the reset control, stores drvdata, and calls `dw_pcie_host_init()`. Host init performs power-on reset, enables the auxiliary clock, asserts `APP_HOLD_PHY_RST`, deasserts power-up reset, writes the PHY lane AC termination values through the CR parameter interface for both PHYs and all four lanes, toggles the aux clock around hold-phy reset release, and sets the device type to RC. Link start temporarily forces advertised link speed to 2.5 GT/s, enables LTSSM, waits for link, restores the original speed capability, requests a speed change, and waits again.

State and persistence behavior: State lives in driver structures and FU740 management/DBI registers. GPIO state controls endpoint PERST and board power. The driver does not persist configuration outside hardware runtime state. Shutdown asserts PERST so firmware/bootloader gets a clean PCIe state after reboot.

Dependencies and integration points: Uses DWC host core and DBI helpers, Linux GPIO consumer APIs, clock and reset frameworks, iopoll, and FU740 management registers. It relies on common DWC MSI setup via the host core and standard PCI Express capability registers for speed manipulation.

Risks: PHY programming uses magic lane offsets and poll timeouts; failures only warn in `fu740_phyregwrite()` and do not abort host init. Link startup mutates read-only PCIe capability fields and must restore DBI RO write protection. The aux clock enable/deassert/re-enable sequence is hardware-specific and easy to break. Optional GPIOs are used without null checks in reset/power helpers, relying on `gpiod_set_value_cansleep()` optional handling. `WARN_ON(ret)` in link start assumes link failures are rare but can be noisy on absent endpoints.

Test signals: On FU740/Unmatched-class hardware, test cold boot and reboot, PERST and power GPIO timing, PHY CR parameter acknowledge polling, aux clock/reset sequencing, initial Gen1 training followed by speed change, MSI enumeration, no-endpoint behavior, and shutdown reset handoff to firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-fu740.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-hisi.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-hisi.c

Purpose: This file implements HiSilicon HIP06/HIP07 "almost ECAM" PCIe configuration-space access. It supplies custom `pci_ecam_ops` for platforms where the Root Port's own config space is mapped through a separate RC base while downstream buses use regular ECAM.

Important APIs, types, and functions: `struct hisi_pcie` stores the Root Complex register base. Config accessors are `hisi_pcie_map_bus()`, `hisi_pcie_rd_conf()`, and `hisi_pcie_wr_conf()`. ACPI initialization is `hisi_pcie_init()` and exports `const struct pci_ecam_ops hisi_pcie_ops`. Device-tree platform initialization is `hisi_pcie_platform_init()` with `hisi_pcie_platform_ops` passed to `pci_host_common_probe()`.

Control flow: For config accesses on the root bus, map returns `pcie->reg_base + where` and read/write restrict access to slot 0 using the 32-bit generic accessors. For subordinate buses, map/read/write delegate to standard ECAM helpers. ACPI init allocates state, finds RC resources from a `HISI0081` ACPI device with matching segment, remaps config space, and stores it in `cfg->priv`. DT init maps `reg[1]` as the RC base and stores it in `cfg->priv`. The platform driver matches HIP06/HIP07 ECAM compatibles and delegates probe to the common PCI host driver.

State and persistence behavior: State is limited to `cfg->priv` and the remapped RC base for the lifetime of the PCI config window. There is no durable state and no DWC runtime resource sequencing in this file.

Dependencies and integration points: Integrates with Linux PCI ECAM, ACPI PCI root/resource quirks, `pci-host-common`, platform resources, and generic PCI config-space accessors. It does not include `pcie-designware.h` because it operates at the ECAM access layer rather than through the DWC host core.

Risks: Root bus slot filtering is essential; exposing nonzero devices on the root bus would create fake config devices. ACPI resource lookup must match the segment or config space maps the wrong controller. The root port requires 32-bit config accessors while downstream ECAM can use normal width accesses; mixing those paths can break config cycles. The code is compiled under conditional ACPI/DT Kconfig combinations, so declarations must remain guarded consistently.

Test signals: Test HIP06/HIP07 DT and ACPI boot, root bus slot 0 read/write, root bus nonzero slot returning device-not-found, downstream ECAM enumeration, ACPI segment matching, missing `reg[1]` failure, and common host probe integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-hisi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-histb.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-histb.c

Purpose: This is the HiSilicon STB DesignWare PCIe root-complex driver for `hi3798cv200-pcie`. It controls STB system registers, DBI access sideband enable bits, Root Port config operations, link-up/LTSSM detection, clocks, resets, optional regulator, optional PHY, and endpoint reset GPIO.

Important APIs, types, and functions: `struct histb_pcie` stores a pointer to `struct dw_pcie`, four clocks, optional PHY and regulator, three resets, control register base, and reset GPIO. Vendor DBI callbacks are `histb_pcie_read_dbi()` and `histb_pcie_write_dbi()`, using sideband functions `histb_pcie_dbi_r_mode()` and `histb_pcie_dbi_w_mode()`. Host callbacks include `histb_pcie_host_init()`, `histb_pcie_start_link()`, and `histb_pcie_link_up()`. Local Root Port config ops are `histb_pcie_rd_own_conf()` and `histb_pcie_wr_own_conf()`.

Control flow: Probe allocates wrapper and DWC structures, maps `control` and `rc-dbi`, obtains optional `vpcie`, reset GPIO, clocks, resets, and optional PHY, then powers/enables the host. `histb_pcie_host_enable()` enables regulator, releases endpoint reset GPIO, enables bus/sys/pipe/aux clocks, pulses soft/sys/bus resets, and returns. DWC host init calls `histb_pcie_host_init()`, which installs custom bridge ops and sets RC work mode. Link start sets the LTSSM enable bit. Link-up requires XMLH link-up, RDLH link-up, and LTSSM state active.

State and persistence behavior: Runtime state consists of mapped hardware registers, clock/reset/regulator/PHY enablement, and DWC host state. DBI reads/writes temporarily toggle sideband enable bits and do not persist beyond each transaction. Remove disables host resources and exits the PHY. There is no persistent storage.

Dependencies and integration points: Uses DWC host core, PCI bridge ops, Linux clocks, resets, optional regulator, GPIO, PHY, platform resources, and HiSTB system registers. It integrates custom root-bus config access by assigning `pp->bridge->ops`.

Risks: The driver must gate DBI access through separate read/write sideband bits; missing disable could expose unintended register access, while missing enable breaks config cycles. Error handling in probe jumps to PHY exit but does not call `histb_pcie_host_disable()` after a `dw_pcie_host_init()` failure, so changes there need care. `gpiod_set_consumer_name()` is called on an optional descriptor and depends on GPIO helper behavior. Link-up uses three conditions, preventing false positives but making hardware status bit changes visible as enumeration failures.

Test signals: Validate STB probe with and without optional regulator/PHY, clock/reset sequencing, Root Port config slot filtering, DBI sideband read/write, RC mode selection, LTSSM link-up detection, remove cleanup, and failures at each clock/reset/regulator acquisition point.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-histb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-intel-gw.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-intel-gw.c

Purpose: This is the Intel Gateway/LGM DesignWare PCIe root-complex driver. It sequences an application register block, core clock/reset, PHY, endpoint reset GPIO, link setup, integrated interrupt enables, L2 entry on shutdown/suspend, and noirq suspend/resume.

Important APIs, types, and functions: `struct intel_pcie` embeds `struct dw_pcie` and stores app register base, endpoint reset GPIO, reset interval, core clock/reset, and PHY. Helpers include `pcie_update_bits()`, app/DBI masked write wrappers, `intel_pcie_ltssm_enable()`, `intel_pcie_ltssm_disable()`, `intel_pcie_link_setup()`, `intel_pcie_init_n_fts()`, reset helpers, `intel_pcie_wait_l2()`, `intel_pcie_turn_off()`, and `intel_pcie_host_setup()`. Host callback `intel_pcie_rc_init()` calls setup through DWC host ops.

Control flow: Probe allocates the controller, sets `use_parent_dt_ranges`, gets clock/reset/app/PHY resources, initializes endpoint reset GPIO, installs DWC ops and host ops, and calls `dw_pcie_host_init()`. Host setup asserts core and endpoint reset, initializes PHY, deasserts core reset, enables core clock, sets `atu_base` to `dbi_base + 0xC0000`, disables LTSSM, disables link disable/ASPM controls, sets N_FTS based on max speed, runs `dw_pcie_setup_rc()` and `dw_pcie_upconfig_setup()`, releases endpoint reset, enables LTSSM, waits for link, and enables integrated interrupts. Remove deinitializes DWC host, disables interrupts, turns off link, disables clock/reset/PHY. Suspend disables interrupts, waits for L2 for Gen3+, exits PHY and disables clock; resume reruns host setup.

State and persistence behavior: State is volatile. Hardware registers hold LTSSM, PM turnoff, interrupt enable/clear, and link setup. The reset interval can come from `reset-assert-ms`, defaulting to 100 ms. No persistent storage is used. Suspend state is reconstructed by `intel_pcie_host_setup()` on resume.

Dependencies and integration points: Uses DWC host core, PHY, clock, reset, GPIO, device properties, iopoll, PCIe capability DBI access, and Intel application registers. Integrated interrupts are enabled in hardware but MSI/INTx handling is otherwise delegated to the DWC/PCI host layers.

Risks: `intel_pcie_host_setup()` manually calls `dw_pcie_setup_rc()` inside the host `init` callback rather than relying only on generic flow; ordering with DWC host init must remain compatible. L2 wait is only attempted for Gen3+ and can delay suspend/remove up to five seconds. `atu_base` is hard-coded relative to DBI. Endpoint reset polarity is active-high assert and active-low release. Interrupt bits must be cleared before disabling to avoid stale events across resume.

Test signals: Test LGM probe, link training, ATU translation, Gen1/Gen2/Gen3/Gen4 N_FTS programming, integrated interrupt enable/clear, remove path, noirq suspend/resume with link present and absent, L2 timeout handling, `reset-assert-ms` override, and resource failure unwinds for PHY/clock/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-intel-gw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-keembay.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-keembay.c

Purpose: This is the Intel Keem Bay DesignWare PCIe driver supporting both root-complex and endpoint modes. It configures APB registers, master/aux clocks, internal PLL, endpoint reset GPIO in host mode, custom MSI interrupt acknowledgement in host mode, endpoint interrupt capabilities, and DWC link callbacks.

Important APIs, types, and functions: `struct keembay_pcie` embeds `struct dw_pcie` and stores APB base, mode, clocks, and reset GPIO. Link callbacks are `keembay_pcie_link_up()`, `keembay_pcie_start_link()`, and `keembay_pcie_stop_link()`. Host helpers include `keembay_pcie_probe_clocks()`, `keembay_pcie_pll_init()`, `keembay_pcie_msi_irq_handler()`, `keembay_pcie_setup_msi_irq()`, and `keembay_pcie_add_pcie_port()`. Endpoint callbacks are `keembay_pcie_ep_init()`, `keembay_pcie_ep_raise_irq()`, and `keembay_pcie_get_features()`.

Control flow: Probe maps APB registers and branches by OF-selected mode. RC mode sets host ops, marks `msi_irq[0]` invalid so the custom chained IRQ path is used, installs the `pcie` IRQ handler, obtains reset GPIO, enables master and 24 MHz aux clocks, bypasses PHY SRAM, sets RC device type, initializes and polls the low-jitter PLL, deasserts controller reset, releases endpoint reset, calls `dw_pcie_host_init()`, then enables MSI controller interrupts if MSI is configured. EP mode installs endpoint ops, calls `dw_pcie_ep_init()` and `dw_pcie_ep_init_registers()`, and notifies EPC. Link start for RC disables LTSSM, waits for PHY MPLLA lock, then enables LTSSM; EP start is a no-op.

State and persistence behavior: State is in driver memory, APB registers, and DWC endpoint/host structures. Clocks use devm action cleanup. Host reset GPIO controls downstream PERST. Endpoint initialization enables eDMA interrupts in APB. There is no persistent storage or explicit remove path.

Dependencies and integration points: Uses DWC host/endpoint core, Linux clocks, GPIO, chained IRQ handling, platform resources, and Keem Bay APB/PLL registers. MSI dispatch integrates by calling `dw_handle_msi_irq()` after filtering APB interrupt status and clearing Keem Bay-specific status bits.

Risks: The host MSI path relies on an extra APB status clear after `dw_handle_msi_irq()`. PLL and PHY lock polling are mandatory before LTSSM. Endpoint mode does not initialize clocks/PLL in this file, so platform/firmware assumptions matter. INTx is explicitly unsupported in endpoint mode and must return `-EINVAL`. BAR feature restrictions expose only 64-bit BAR0/2/4 with 16 KiB alignment.

Test signals: Test RC and EP compatibles, master/aux clock enable and aux rate setting, PLL lock timeout, host link-up bits, MSI delivery/clear, endpoint MSI/MSI-X raising and INTx rejection, endpoint BAR alignment/features, EP register initialization, and absent endpoint/no-link handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-keembay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-kirin.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-kirin.c

Purpose: This is the HiSilicon Kirin phone SoC DesignWare PCIe root-complex driver for Kirin 960 and Kirin 970. It handles APB regmap access, sideband DBI enable, internal Hi3660 PHY setup for Kirin 960, external PHY support for Kirin 970, DWC and per-slot PERST GPIOs, optional per-slot clock-enable GPIOs, custom Root Port config ops, and link start/status.

Important APIs, types, and functions: `struct kirin_pcie` stores PHY type, DWC pointer, APB regmap, PHY/private PHY data, DWC PERST GPIO, per-slot reset GPIOs/names, and per-slot CLKREQ GPIOs/names. `struct hi3660_pcie_phy` stores internal PHY resources and clocks. Internal PHY helpers include `hi3660_pcie_phy_get_clk()`, `hi3660_pcie_phy_get_resource()`, `hi3660_pcie_phy_clk_ctrl()`, `hi3660_pcie_phy_power_on()`, and `hi3660_pcie_phy_power_off()`. DWC callbacks include `kirin_pcie_read_dbi()`, `kirin_pcie_write_dbi()`, `kirin_pcie_link_up()`, and `kirin_pcie_start_link()`. Host bus ops include `kirin_pcie_rd_own_conf()`, `kirin_pcie_wr_own_conf()`, and `kirin_pcie_add_bus()`.

Control flow: Probe selects internal or external PHY data, allocates wrapper and DWC structures, maps APB as a regmap, gets the DWC reset GPIO, parses optional `hisilicon,clken` GPIOs, walks child PCI nodes to find per-slot reset GPIOs and names, stores drvdata, powers on the PHY, asserts DWC PERST, waits required timing, then calls `dw_pcie_host_init()`. Internal PHY power-on enables CMOS power, output enable/debounce, clocks, isolation/clock gates, and PHY start. External PHY mode obtains and powers a generic PHY. Host init installs custom bridge ops. When a PCI bus is added, per-slot PERST GPIOs are asserted after bridge enumeration. Link start writes LTSSM enable through APB; link-up checks APB PHY status bits.

State and persistence behavior: State is volatile and reconstructed on probe. APB sideband bits are toggled around each DBI transaction. GPIOs hold DWC bridge PERST, per-slot PERST, and optional clock-request state. Remove deinitializes DWC host and powers off PHY/clocks. There is no durable storage.

Dependencies and integration points: Uses DWC host core, PCI bridge operations, Linux regmap/syscon, OF PCI child parsing, GPIO descriptors, generic PHY, clock framework, and Hi3660 sysctrl/crgctrl registers. Kirin 960 retains an embedded PHY driver because the DT schema cannot be split into a separate PHY provider.

Risks: Several timing delays are hardware contract values. Internal PHY stable-clock check is subtle and the code returns timeout if the status bit indicates not-ready according to SoC semantics. Per-slot parsing must not exceed `MAX_PCI_SLOTS`; the current check happens after indexing, so changes should be careful around bounds. DBI sideband enable/disable must bracket each config access. Per-slot reset behavior is tied to Hikey970 topology with a PEX switch; generic changes can affect downstream slots.

Test signals: Test Kirin 960 internal PHY and Kirin 970 external PHY boot, APB DBI read/write, root slot filtering, child-node reset GPIO parsing, per-slot PERST assertion in `add_bus`, optional clock-enable GPIO behavior, link-up detection, PHY power-off on remove, and failure unwinds for missing syscon/clocks/PHY/GPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-kirin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-nxp-s32g.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-nxp-s32g.c

Purpose: This is the NXP S32G DesignWare PCIe root-complex driver. It configures S32G controller registers, per-port SerDes PHYs, root-port mode, LTSSM, Gen3/SRIS-related DWC settings, ACE coherency boundaries, runtime PM, and DWC host integration.

Important APIs, types, and functions: `struct s32g_pcie` embeds `struct dw_pcie`, controller register base, and parsed port list. `struct s32g_pcie_port` stores a SerDes PHY. DWC link ops are `s32g_pcie_start_link()` and `s32g_pcie_stop_link()`. Host initialization is `s32g_init_pcie_controller()`. PHY lifecycle is handled by `s32g_init_pcie_phy()` and `s32g_deinit_pcie_phy()`. Port parsing is `s32g_pcie_parse_ports()` and `s32g_pcie_parse_port()`.

Control flow: Probe allocates state, maps `ctrl`, parses child `pci` nodes for PHYs and optional `num-lanes`, enables runtime PM, disables LTSSM, initializes each SerDes PHY in PCIe mode and powers it on, sets host ops and `pp->use_atu_msg`, then calls `dw_pcie_host_init()`. Host init sets Root Port device type, clears SRIS mode to use default CRNS, resets DWC ACE coherency registers so peripheral space below 0x80000000 is non-coherent and DDR above it is memory, enables SRIS deskew and Gen3 phase 2/3 equalization, and returns. DWC start/stop toggles the LTSSM bit.

State and persistence behavior: State is volatile. Hardware registers keep LTSSM, device type, SRIS, coherency, and DWC Gen3 setup while powered. The ports list owns PHY lifecycle until deinit. Runtime PM is active after successful probe. Suspend/resume delegates to DWC noirq helpers.

Dependencies and integration points: Uses DWC host core, Linux PHY framework with `phy_set_mode_ext(PHY_MODE_PCIE, 0)`, runtime PM, OF child parsing, and S32G control registers. DWC coherency registers from `pcie-designware.h` are programmed directly.

Risks: ACE coherency setup is required for MSI/peripheral traffic because Ncore can drop coherent transactions to peripheral space. Hard-coded DDR boundary at 0x80000000 must match platform memory layout. PHY error unwinding deletes the ports list, so later cleanup must avoid double-use. The driver assumes one Root Port for `num-lanes` propagation. `pp->use_atu_msg` affects PME/message ATU behavior and should not be removed casually.

Test signals: Test S32G2 probe with valid `pci` child nodes, SerDes PHY init/mode/power sequencing, no-child error path, `num-lanes` propagation, coherency register programming, MSI delivery, LTSSM start/stop, Gen3 link training, runtime PM suspend/resume, and PHY failure unwinds across multiple ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-nxp-s32g.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-qcom-common.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-qcom-common.c

Purpose: This file provides shared Qualcomm DesignWare PCIe tuning helpers used by Qualcomm RC and EP drivers. It programs DWC Gen3+ equalization settings and Gen4 16 GT/s lane-margining capability registers.

Important APIs, types, and functions: `qcom_pcie_common_set_equalization()` iterates from 8.0 GT/s to the controller max link speed and programs `GEN3_RELATED_OFF`, `GEN3_EQ_FB_MODE_DIR_CHANGE_OFF`, and `GEN3_EQ_CONTROL_OFF`. `qcom_pcie_common_set_16gt_lane_margining()` programs `GEN4_LANE_MARGINING_1_OFF` and `GEN4_LANE_MARGINING_2_OFF`. Both symbols are exported GPL for use by multiple Qualcomm PCIe modules.

Control flow: Equalization selects a rate shadow for each supported speed, clears noncompliance and EQ fields, sets timing/evaluation/cursor-delta values, and clears phase/control vectors. The loop stops and warns if the derived speed exceeds 32.0 GT/s. Lane margining clears existing max offset/step fields, writes Qualcomm values for voltage and timing, advertises independent error sampler and reporting method, clears unsupported vertical voltage indication, and writes max lanes and sample rates from `pci->num_lanes`.

State and persistence behavior: State is hardware-register state only. The helpers modify DBI registers on the active controller and do not store driver-private state. Their effects are re-applied by RC/EP link bring-up paths.

Dependencies and integration points: Depends on `pcie-designware.h` DWC DBI helpers and register definitions, Linux PCI link speed helpers, and `struct dw_pcie`. Called from `pcie-qcom.c` and `pcie-qcom-ep.c` before enabling LTSSM/link training.

Risks: These helpers write low-level PHY/link training policy across data rates. Incorrect field values can break Gen3/Gen4 link training or margining reporting. The equalization loop depends on `pcie_get_link_speed(pci->max_link_speed)` returning an encoded PCI speed compatible with the loop bounds. Register access assumes DBI is available and writable at the call point.

Test signals: On Qualcomm RC and EP hardware, test Gen3, Gen4, and higher max-speed configurations; confirm link training succeeds at target speeds, no warning occurs for supported speeds, 16 GT/s lane margining registers advertise expected lane counts, and repeated link bring-up reprograms consistent values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-qcom-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-qcom-common.h -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-qcom-common.h

Purpose: This header declares the shared Qualcomm PCIe helper API for equalization and 16 GT/s lane margining.

Important APIs, types, and functions: It forward-declares `struct dw_pcie` and declares `qcom_pcie_common_set_equalization()` and `qcom_pcie_common_set_16gt_lane_margining()`.

Control flow: The header has no execution. Including drivers call the declared helpers during link setup when DBI registers are accessible and before link training or speed-dependent capability exposure is finalized.

State and persistence behavior: No state is declared in the header. Hardware effects are in the corresponding C implementation.

Dependencies and integration points: Used by Qualcomm root-complex and endpoint drivers alongside `pcie-designware.h`. The forward declaration keeps include coupling small while preserving type checking for function parameters.

Risks: Prototype drift from `pcie-qcom-common.c` would break builds for both Qualcomm drivers. Adding helper declarations here makes them part of the internal Qualcomm DWC glue API and should preserve DBI availability assumptions.

Test signals: Build `pcie-qcom.c`, `pcie-qcom-ep.c`, and `pcie-qcom-common.c` together and as modules/built-ins under relevant Kconfig combinations to catch missing prototypes or export mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-qcom-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-qcom-ep.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-qcom-ep.c

Purpose: This is the Qualcomm DesignWare PCIe endpoint controller driver. It manages endpoint DBI/PARF/MMIO resources, PERST-driven resource enable/disable, firmware-managed variants, clocks/resets/PHY/interconnect bandwidth, endpoint initialization, global event IRQs, PERST IRQs, debugfs link counters, endpoint IRQ raising, HDMA settings, and Qualcomm link/power-management PARF programming.

Important APIs, types, and functions: `struct qcom_pcie_ep` embeds `struct dw_pcie` and stores PARF/MMIO resources, optional PERST syscon, core reset, PERST and WAKE GPIOs, PHY, debugfs, interconnect path, clocks, SoC config, link status, and IRQ numbers. DWC ops are `qcom_pcie_dw_link_up()`, `qcom_pcie_dw_start_link()`, `qcom_pcie_dw_stop_link()`, and `qcom_pcie_dw_write_dbi2()`. Major lifecycle functions are `qcom_pcie_perst_deassert()`, `qcom_pcie_perst_assert()`, `qcom_pcie_enable_resources()`, `qcom_pcie_disable_resources()`, `qcom_pcie_ep_probe()`, and `qcom_pcie_ep_remove()`. IRQ handlers are `qcom_pcie_ep_global_irq_thread()` and `qcom_pcie_ep_perst_irq_thread()`.

Control flow: Probe allocates state, installs DWC and endpoint ops, applies HDMA eDMA settings for matching SoCs, sets runtime PM active, maps PARF/DBI/MMIO and optional PERST syscon, gets PERST input and optional WAKE output, obtains clocks/reset/PHY/interconnect unless firmware-managed, initializes the DWC endpoint controller, requests global and PERST threaded IRQs, drops runtime PM to suspend, and creates debugfs. DWC start_link enables the PERST IRQ rather than immediately training the link. When the host deasserts PERST, the PERST IRQ calls `qcom_pcie_perst_deassert()`, which resumes runtime PM, enables resources if needed, cleans prior endpoint state, pulses WAKE, configures TCSR PERST separation, disables BDF-to-SID, sets EP device type and power/link registers, configures DBI capability latencies, masks/enables relevant PARF interrupts, initializes endpoint registers, applies Qualcomm equalization and Gen4 lane margining if needed, programs MHI base, notifies EPC, and enables LTSSM. When PERST asserts, resources are disabled and link status becomes disabled.

State and persistence behavior: Driver state is volatile. `link_status` records disabled/enabled/up/down transitions from PERST and global interrupts. Runtime PM and interconnect bandwidth are adjusted as resources are enabled or disabled. PARF registers keep endpoint mode, interrupt masks, MHI base, no-snoop override, L1/L1SS behavior, and clock-gating policy while active. Debugfs exposes link transition counters from MMIO. No durable storage is used.

Dependencies and integration points: Integrates with DWC endpoint core, PCI EPC notification APIs, Qualcomm common equalization helpers, Linux clocks, resets, PHY, runtime PM, interconnect, GPIO, syscon/regmap, debugfs, platform IRQs, and optional HDMA/eDMA support. Endpoint features advertise linkup notifications, MSI capability, 4 KiB alignment, and 64-bit BAR0/BAR2.

Risks: The driver is heavily event-driven; wrong PERST IRQ polarity toggling or runtime PM ordering can leave the endpoint invisible or powered during host reset. Firmware-managed configs skip local clocks/resets/PHY, so resource paths must respect that flag. Global IRQ status is handled as an if/else chain, so simultaneous bits prioritize the first matched event. `qcom_pcie_ep_get_resources()` can overwrite `ret` while collecting optional PHY/interconnect errors, so changes must preserve intended optionality. DBI2 access requires temporary ELBI CS2 enable. PARF power-management and no-snoop settings affect cache coherency, L1SS, MHI, and PM turn-off behavior.

Test signals: Test each compatible including firmware-managed SA8255P and HDMA/no-snoop SA8775P. Exercise PERST assert/deassert cycles, runtime PM transitions, WAKE pulse, endpoint enumeration, linkup/linkdown/BME/D-state/PM turnoff events, interconnect bandwidth update after BME, INTx/MSI raise paths, debugfs counters, MHI BAR base programming, no-snoop override, MHI parity mask disabling, Gen4 lane margining, remove while link disabled/enabled, and failures in resource enable, endpoint register init, and IRQ request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-qcom-ep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-qcom.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-qcom.c

Purpose: This is the Qualcomm DesignWare PCIe root-complex driver. It supports many Qualcomm PCIe IP revisions with per-revision resource/init/deinit callbacks, optional firmware-managed ECAM mode, PERST parsing from Root Port or legacy bindings, PHY and power-control device sequencing, OPP/interconnect bandwidth management, link tuning, BDF-to-SID programming, debugfs link counters, and suspend/resume.

Important APIs, types, and functions: `struct qcom_pcie` stores DWC pointer, PARF/MHI bases, revision-specific resource union, interconnect paths, config, debugfs, parsed ports, suspend state, and OPP mode. `struct qcom_pcie_cfg` selects `struct qcom_pcie_ops` plus no-snoop, firmware-managed, and no-L0s flags. Revision callbacks include resource/init/post_init/deinit/ltssm/config_sid variants for IP 1.0.0, 2.1.0, 2.3.2, 2.3.3, 2.4.0, 2.7.0, 1.9.0/1.21.0/1.34.0, and 2.9.0. Main DWC callbacks are `qcom_pcie_start_link()` and `qcom_pcie_link_up()`. Host callbacks are `qcom_pcie_host_init()`, `qcom_pcie_host_deinit()`, and `qcom_pcie_host_post_init()`.

Control flow: Probe enables runtime PM. Firmware-managed configs allocate a host bridge, create an ECAM config window with Qualcomm MSI init, and call `pci_host_probe()`. Native configs allocate DWC and Qualcomm state, map PARF and optional MHI, initialize either OPP or interconnect bandwidth, call revision `get_resources`, parse Root Port child nodes for PHY and PERST GPIOs or fall back to legacy `pciephy`/`perst`, install DWC host ops, and call `dw_pcie_host_init()`. Host init asserts all PERST GPIOs, runs revision init, powers PHYs, creates and powers PCI pwrctrl devices, runs revision post-init, clears L0s if configured, removes unsupported MSI-X and DPC capabilities, deasserts PERST, and optionally programs BDF-to-SID mapping. DWC link start applies Qualcomm equalization, Gen4 lane margining for 16 GT/s, and revision LTSSM enable. After host init, bandwidth/OPP is updated from negotiated link width/speed.

State and persistence behavior: State is volatile. Revision resource unions hold clocks, resets, and regulators. Port lists hold PHYs and PERST GPIOs. Runtime PM, interconnect votes, and OPP votes represent current power/performance state. `suspended` tracks whether resources were turned off because no link was active. PARF registers retain DBI/ATU base, device type, wake/clock gating, no-snoop override, MHI, BDF/SID table, and link tuning while active. Debugfs exposes MHI link transition counters when the MHI region exists.

Dependencies and integration points: Integrates with DWC host core, PCI ECAM/common host code for firmware-managed mode, PCI pwrctrl child devices, PHY framework, clocks/resets/regulators, GPIO, runtime PM, interconnect, OPP, debugfs, OF child/legacy bindings, PCI fixups, and Qualcomm common equalization helpers. MSI support uses DWC MSI host init in firmware-managed ECAM mode and normal DWC host setup in native mode.

Risks: This file has broad SoC coverage and many revision-specific sequences; changing common flow can regress older IP revisions. PERST parsing is recursive and rejects shared PERST because gpiolib exclusive access is required. BDF-to-SID programming uses a CRC8 hash table and collision chaining; mistakes break IOMMU stream IDs. Suspend keeps resources on when a link is active to avoid config/MSI access violations late in suspend; changing this can cause NoC/access faults or storage device power-loss issues. Interconnect/OPP updates must match link state and suspend target. Removing MSI-X/DPC capabilities and clearing L0s are compatibility workarounds that affect enumeration and ASPM policy.

Test signals: Test representative compatibles for every revision config plus firmware-managed SA8255P. Exercise Root Port child parsing and legacy binding fallback, multiple PERST GPIOs, PHY init/power failure unwinds, pwrctrl device creation/power-on/off, link training at Gen1-Gen4, equalization/lane margining, BDF-to-SID with collision cases, no-snoop override, L0s clearing, ECAM firmware-managed MSI init, OPP table present/absent, interconnect bandwidth update after link, debugfs counters, suspend/resume with link up and link down, and PCI class fixups for Qualcomm device IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-qcom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-rcar-gen4.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-rcar-gen4.c

Purpose: This is the Renesas R-Car Gen4 DesignWare PCIe controller driver supporting RC and EP mode. It manages Renesas application/PHY registers, runtime PM, core clocks/resets, mode selection, bifurcation, link control, speed change retries, host PERST/MSI enable, endpoint EPC features, eDMA interrupt enablement, multi-function DBI offsets, R-Car V4H and generic Gen4 LTSSM flows, and PHY firmware download.

Important APIs, types, and functions: `struct rcar_gen4_pcie` embeds `struct dw_pcie` and stores app/PHY bases, platform device, and drvdata. `struct rcar_gen4_pcie_drvdata` selects additional init, LTSSM control, and mode. Common callbacks include `rcar_gen4_pcie_link_up()`, `rcar_gen4_pcie_start_link()`, `rcar_gen4_pcie_stop_link()`, `rcar_gen4_pcie_common_init()`, and `rcar_gen4_pcie_common_deinit()`. Host functions include `rcar_gen4_pcie_host_init()` and `rcar_gen4_pcie_host_deinit()`. Endpoint functions include `rcar_gen4_pcie_ep_pre_init()`, `rcar_gen4_pcie_ep_raise_irq()`, feature reporting, and DBI/DBI2 offset callbacks. PHY-specific functions include `rcar_gen4_pcie_ltssm_control()` and `rcar_gen4_pcie_download_phy_firmware()`.

Control flow: Probe allocates the wrapper, sets DWC ops, marks eDMA unroll mode and required resources capability, maps `phy` and `app`, enables runtime PM, then adds either RC or EP based on match data. Common init enables core clocks, asserts/deasserts power reset with mandated delay/status readback, selects RC or EP mode in `PCIEMSR0`, enables bifurcation if lanes < 4, applies additional init if configured, and returns. RC init asserts PERST, runs common init, clears Root Port BAR0/BAR1 through DBI2, enables MSI interrupt signal, waits 100 ms, releases PERST, and lets DWC host proceed. EP pre-init runs common init and enables DMA interrupt status bits; endpoint registration initializes DWC EPC and registers.

State and persistence behavior: State is runtime hardware state and DWC host/endpoint structures. `drvdata` determines mode and LTSSM control path. Runtime PM remains enabled after probe. The driver writes firmware contents into PHY/port-logic registers during LTSSM enable for generic Gen4 variants; the firmware is loaded from `rcar_gen4_pcie.bin` at runtime but not persisted by the driver. Remove deinitializes the selected DWC role and disables runtime PM.

Dependencies and integration points: Uses DWC host/endpoint core, eDMA unroll mode, Linux firmware loader, runtime PM, reset/clock resources from DWC resource acquisition, GPIO PERST from `dw->pe_rst`, platform resources, and Renesas app/PHY registers. Endpoint features integrate with PCI EPC and support MSI but not MSI-X in this driver.

Risks: Reset sequencing protects against SError during DBI access; removing status readback/delay is hazardous. The generic Gen4 LTSSM path uses datasheet magic PHY offsets and firmware polling loops; missing firmware or timeout prevents link training. Speed-change retry logic intentionally ignores failures after some attempts, especially EP mode where the link may not yet be connected. Endpoint `ep_pre_init()` cannot return errors, so common-init failures are silently returned from the callback body. BAR feature layout and DBI function offsets are hardware ABI for endpoint functions.

Test signals: Test R-Car V4H and generic Gen4 RC/EP compatibles, firmware-present and firmware-missing paths, reset/clock runtime PM sequencing, bifurcation with lane counts below four, host PERST and MSI enable, link-up status bits, Gen2/Gen3/Gen4 speed changes, endpoint init/registers, endpoint INTx/MSI raising, BAR features, function DBI/DBI2 offsets, eDMA interrupt enable/disable, and remove cleanup in both modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-rcar-gen4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-sophgo.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-sophgo.c

Purpose: This is the Sophgo SG2044 DesignWare PCIe host-controller driver. It maps Sophgo app registers, enables clocks, creates a legacy INTx IRQ domain with chained IRQ dispatch, enables MSI signaling, disables ASPM L0s/L1 capability advertisement, and initializes the DWC root complex.

Important APIs, types, and functions: `struct sophgo_pcie` embeds `struct dw_pcie` and stores app register base, clocks, and INTx IRQ domain. App accessors are `sophgo_pcie_readl_app()` and `sophgo_pcie_writel_app()`. IRQ flow is implemented by `sophgo_pcie_intx_handler()`, `sophgo_intx_irq_mask()`, `sophgo_intx_irq_unmask()`, `sophgo_pcie_intx_map()`, and `sophgo_pcie_init_irq_domain()`. Host setup helpers are `sophgo_pcie_msi_enable()`, `sophgo_pcie_disable_l0s_l1()`, `sophgo_pcie_host_init()`, `sophgo_pcie_clk_init()`, and `sophgo_pcie_configure_rc()`.

Control flow: Probe allocates state, stores drvdata, maps the `app` region, enables all clocks using `devm_clk_bulk_get_all_enabled()`, then configures RC mode by setting DWC host ops and calling `dw_pcie_host_init()`. Host init obtains the child `interrupt-controller` fwnode, gets its IRQ, creates a four-entry INTx domain, installs a chained handler, clears L0s/L1 ASPM bits from the PCIe Link Capabilities register under DBI read-only write enable, and sets the MSI enable bit in the Sophgo interrupt-enable register. INTx mask/unmask update per-line bits under the DWC root-port raw spinlock.

State and persistence behavior: Runtime state is app-register interrupt enable/mask state, IRQ domain mappings, clock enablement, and DWC host state. There is no durable state and no explicit remove callback; devm resources and built-in driver lifetime are relied upon.

Dependencies and integration points: Uses DWC host core, Linux clock bulk APIs, IRQ domains/chained IRQs, fwnode child lookup, platform resources, and PCI DBI capability editing. It relies on DWC MSI handling while Sophgo app registers gate the MSI interrupt signal.

Risks: INTx status bits are read from a field shifted into bits 8:5; wrong field handling would dispatch wrong hwirqs. Mask/unmask share one app register with MSI enable and must preserve unrelated bits under lock. ASPM L0s/L1 are forcibly hidden, likely due to hardware issues; re-enabling can destabilize links. Missing child interrupt controller or IRQ causes host init failure.

Test signals: Test SG2044 probe, clock enablement, INTx child fwnode parsing, chained INTx delivery and mask/unmask, MSI interrupt delivery, ASPM capability clearing visible in config space, absent interrupt-controller failure, and concurrent INTx/MSI enable register updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-sophgo.c -->
