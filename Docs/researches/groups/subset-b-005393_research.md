# Research: subset-b-005393

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spmi/spmi-pmic-arb.c -->
# sources/distributed-fs/ceph-client/drivers/spmi/spmi-pmic-arb.c

## Purpose
Qualcomm PMIC Arbiter platform driver implementing an SPMI controller plus a PMIC interrupt controller. It registers one or more `spmi_controller` instances, translates SPMI command APIs into PMIC Arbiter register transactions, maps PPID/APID ownership tables for arbiter hardware versions v1/v2/v3/v5/v7/v8, and exposes QPNP peripheral IRQs through an irqdomain.

## Important APIs, Types, and Functions
Key state is `struct spmi_pmic_arb` for shared hardware resources/version ops and `struct spmi_pmic_arb_bus` for each SPMI bus instance, including `spmic`, IRQ domain, `ppid_to_apid`, `apid_data`, APID bounds, and MMIO bases. `struct pmic_arb_ver_ops` abstracts version-specific resource mapping, APID init, PPID lookup, command formatting, offset calculation, and interrupt register addressing. SPMI entry points are `pmic_arb_cmd`, `pmic_arb_read_cmd`, `pmic_arb_write_cmd`; interrupt chip callbacks are `qpnpint_irq_ack`, mask/unmask/type/wake/get-state plus domain translate/alloc/activate. Probe/remove are `spmi_pmic_arb_probe` and `spmi_pmic_arb_remove`.

## Control Flow
Probe maps the `core` resource, reads `PMIC_ARB_VERSION`, selects a `pmic_arb_v*` ops table, maps observer/channel/core resources, reads DT `qcom,channel` and `qcom,ee`, then registers legacy or child `spmi` bus nodes. Bus init allocates a controller, maps `cnfg`/`intr` and optional v8 `chnl_owner`, builds APID state, creates an irqdomain, installs a chained IRQ handler, and adds the SPMI controller. Data transfers format opcode/address/count, compute version-specific channel offset from SID/address/APID, serialize with `raw_spin_lock_irqsave`, write/read data FIFOs, issue command, and poll `PMIC_ARB_STATUS_DONE`. IRQ flow enters `pmic_arb_chained_irq`, scans owner access status over APID ranges, dispatches each status bit to mapped virqs, and falls back to per-APID IRQ status if owner status was empty.

## State and Persistence
Runtime state is memory-resident and device-managed: APID/PPID caches, mapping validity bitmap, APID owner data, min/max APID bounds learned during IRQ translation, and bus count. Hardware state persists in PMIC Arbiter register windows and PMIC interrupt registers; the driver clears latched/enable registers during IRQ activation and ack. Remove unregisters chained handlers and irqdomains; devm resources handle mappings/allocations.

## Dependencies and Integration Points
Depends on Linux SPMI core, platform/OF resource parsing, irqdomain/chained IRQ framework, MMIO accessors, and DT bindings that provide `core`, `obsrvr`, `chnls`, `cnfg`, `intr`, optional `chnl_map`/`chnl_owner`, `periph_irq`, `qcom,channel`, and `qcom,ee`. It is consumed by SPMI client drivers through exported SPMI APIs and by OF interrupt consumers using four-cell PMIC IRQ specs.

## Risks
Version-specific offsets and APID ownership rules are the main risk; a wrong ops table, APID count, or v8 owner base can route writes/IRQs to the wrong EE. `spmi_pmic_arb_register_buses` returns `ret` after the child loop without initializing it if no child matches, so DT shape matters. IRQ min/max bounds are only tightened as interrupts are translated, so unmapped APID IRQs rely on fallback cleanup. Polling timeouts, permission failures, and duplicate PPID ownership can surface as `-ETIMEDOUT`, `-EPERM`, or missing interrupts.

## Test Signals
Useful signals are successful probe log with arbiter version, SPMI child device enumeration, working reads/writes up to 8 bytes, rejection of unsupported non-data commands on v2+, correct IRQ domain translation from DT, interrupt ack/mask/unmask behavior, suspend wake propagation to parent IRQ, and no timeout/denied/dropped messages under PMIC traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spmi/spmi-pmic-arb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spmi/spmi.c -->
# sources/distributed-fs/ceph-client/drivers/spmi/spmi.c

## Purpose
SPMI framework core: defines the `spmi` bus type, controller/device lifetime, client driver registration, OF child enumeration, exported SPMI command helpers, tracing, and probe/remove runtime-PM wrapping.

## Important APIs, Types, and Functions
Exports `spmi_device_add/remove/alloc`, `spmi_controller_alloc/add/remove`, `__spmi_driver_register`, `spmi_find_device_by_of_node`, register helpers (`spmi_register_read/write`, `spmi_ext_register_read/write`, `spmi_ext_register_readl/writel`, `spmi_register_zero_write`) and non-data commands (`spmi_command_reset/sleep/wakeup/shutdown`). The bus callbacks are `spmi_device_match`, `spmi_drv_probe`, `spmi_drv_remove`, `spmi_drv_shutdown`, and `spmi_drv_uevent`.

## Control Flow
`postcore_initcall(spmi_init)` registers `spmi_bus_type` and enables controller registration. A controller driver allocates a `spmi_controller`, sets `cmd/read_cmd/write_cmd`, then calls `spmi_controller_add`. The core adds the controller device and, for OF systems, iterates child nodes with two-cell `reg`, validates `SPMI_USID` and slave ID, allocates `spmi_device`, sets fwnode/USID, and calls `device_add`. Client drivers bind by OF match or by device name prefix. Exported register helpers validate width/address limits, route to controller callbacks, and emit tracepoints.

## State and Persistence
Global state is `is_registered` and `ctrl_ida` for numeric controller IDs. Device/controller allocations embed Linux device objects and release via `spmi_dev_release`/`spmi_ctrl_release`. No on-disk state exists; persistence is through driver model references and OF nodes.

## Dependencies and Integration Points
Integrates with Linux driver core, OF, PM runtime, trace events, IDA, and controller implementations such as Qualcomm PMIC Arbiter. SPMI client drivers include `linux/spmi.h` and use the exported helpers rather than controller-private callbacks.

## Risks
Controller callbacks must be set and controller device type must match or all helpers return `-EINVAL`. OF registration rejects malformed `reg` entries and unsupported address types. Probe enables runtime PM before invoking client probe and unwinds on failure; buggy client remove/probe paths can leave usage-count expectations fragile.

## Test Signals
Check `bus_register` succeeds before controller add, OF child devices appear as `<ctrl>-<usid>`, modalias uevents are generated for OF clients, helpers reject invalid lengths/addresses, tracepoints bracket read/write/cmd calls, and controller/device references release without leaks on removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spmi/spmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ssb/Kconfig

## Purpose
Configuration menu for Sonics Silicon Backplane support, host transports, built-in SSB core drivers, embedded support, and optional GPIO/flash/PCI bridge facilities.

## Important APIs, Types, and Functions
This file defines Kconfig symbols rather than C APIs. Core symbols include `SSB`, `SSB_SPROM`, `SSB_BLOCKIO`, host options `SSB_PCIHOST`, `SSB_PCMCIAHOST`, `SSB_SDIOHOST`, `SSB_HOST_SOC`, built-in drivers `SSB_DRIVER_PCICORE`, `SSB_DRIVER_MIPS`, `SSB_DRIVER_EXTIF`, `SSB_DRIVER_GIGE`, `SSB_DRIVER_GPIO`, and feature gates `SSB_SERIAL`, `SSB_SFLASH`, `SSB_EMBEDDED`, `SSB_PCICORE_HOSTMODE`.

## Control Flow
Dependency flow starts with `SSB_POSSIBLE` requiring I/O memory and DMA. `menuconfig SSB` gates all child symbols. Host support is enabled when the relevant subsystem can be built in or as SSB-compatible. Several options select shared support: PCI/PCMCIA/SoC select `SSB_SPROM`; MIPS selects `SSB_SERIAL` and `SSB_SFLASH`; GPIO selects `IRQ_DOMAIN` on embedded builds.

## State and Persistence
Kconfig output persists in the kernel `.config` and controls which object files, code paths, exports, and platform devices are compiled.

## Dependencies and Integration Points
Integrates with PCI, PCMCIA, MMC/SDIO, BCM47XX NVRAM, MIPS, GPIOLIB, and IRQ_DOMAIN. It also coordinates with `Makefile` object selection and preprocessor guards in all SSB files.

## Risks
Wrong dependency combinations can silently omit host support or built-in system core drivers. `SSB_EMBEDDED` depends on MIPS and either no PCI or PCI core hostmode, so embedded watchdog/GPIO/flash behavior is tightly coupled to board architecture. `SSB_B43_PCI_BRIDGE` is hidden and depends on `SSB_PCIHOST`, so wireless bridge registration depends on selecting it elsewhere.

## Test Signals
Validate representative configs: PCI-host wireless, PCMCIA-host wireless, BCM47xx SoC/MIPS, GPIO-only, and SDIO. Build logs should include only expected `ssb-*` objects and no unresolved symbols from disabled transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ssb/Makefile

## Purpose
Build recipe for the monolithic `ssb.o` object, composing core bus code, host transport support, built-in SSB core drivers, and the optional b43 PCI bridge.

## Important APIs, Types, and Functions
No runtime APIs are defined. It maps Kconfig symbols to object files: core `main.o scan.o`; optional `embedded.o`, `sprom.o`, `pci.o`, `pcihost_wrapper.o`, `pcmcia.o`, `bridge_pcmcia_80211.o`, `sdio.o`, `host_soc.o`; built-ins `driver_chipcommon.o`, `driver_chipcommon_pmu.o`, optional sflash, MIPS, EXTIF, PCI core, GigE, GPIO, and b43 bridge.

## Control Flow
Kbuild appends objects into `ssb-y` based on `CONFIG_*`, then links `obj-$(CONFIG_SSB) += ssb.o`. This means most optional subdrivers are linked into the SSB module/built-in image rather than built as separate modules.

## State and Persistence
Build output state is generated object membership. Runtime state is unaffected except through which code is present.

## Dependencies and Integration Points
Must remain synchronized with Kconfig and with init/exit calls in `main.c`, which may call optional functions that are conditionally built or stubbed through headers.

## Risks
Missing object selection causes link failures or disabled runtime features. Including bridge drivers inside `ssb.o` means init errors are logged but often intentionally non-fatal in `main.c`.

## Test Signals
Run builds for `SSB=m`, `SSB=y`, PCI host, PCMCIA host, host SoC/MIPS, and GPIO configurations. Confirm generated `ssb.o` includes the expected object list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/b43_pci_bridge.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/b43_pci_bridge.c

## Purpose
Tiny PCI ID bridge that lets Broadcom 43xx PCI wireless devices be claimed as SSB PCI hosts for b43-era hardware.

## Important APIs, Types, and Functions
Defines `b43_pci_bridge_tbl`, a PCI device ID table for many Broadcom 43xx IDs. Exposes `b43_pci_ssb_bridge_init` and `b43_pci_ssb_bridge_exit`, which call `ssb_pcihost_register`/`ssb_pcihost_unregister` with `b43_pci_bridge_driver`.

## Control Flow
SSB module init invokes bridge init. PCI core matches listed IDs to the driver, and the SSB PCI host wrapper performs the real SSB bus registration. Exit unregisters the PCI driver.

## State and Persistence
No private runtime state; PCI driver registration is the only state. Device ownership is managed by the PCI and SSB host layers.

## Dependencies and Integration Points
Depends on PCI, `ssb_private.h`, and SSB PCI host support. It is not a standalone module despite representing a PCI driver.

## Risks
ID table omissions block SSB discovery for supported wireless cards. Because the driver has no local probe/remove, correctness depends entirely on `ssb_pcihost_register` attaching callbacks. The decimal-looking `43222` device ID is intentional elsewhere in SSB code but is easy to misread.

## Test Signals
PCI modalias table should include listed IDs; on matching hardware, `ssb_pcihost_register` should discover the SSB bus and b43 devices. Init failure should be logged but not prevent the SSB core from loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/b43_pci_bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/bridge_pcmcia_80211.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/bridge_pcmcia_80211.c

## Purpose
PCMCIA host bridge for Broadcom 43xx wireless cards that expose an SSB bus through a PCMCIA memory window.

## Important APIs, Types, and Functions
Defines `ssb_host_pcmcia_tbl`, `ssb_host_pcmcia_probe`, remove, suspend/resume, and public init/exit helpers `ssb_host_pcmcia_init`/`ssb_host_pcmcia_exit`. Probe allocates `struct ssb_bus`, requests/maps a 16-bit memory window, enables IRQ/device, and calls `ssb_bus_pcmciabus_register`.

## Control Flow
Module init registers the PCMCIA driver. Probe configures `CONF_ENABLE_IRQ`, requests resource window 2 sized to `SSB_CORE_SIZE`, maps page zero, verifies IRQ, enables the PCMCIA device, and registers the SSB bus. Error paths disable the device and free the bus. Remove unregisters the SSB bus, disables PCMCIA, frees memory, and clears `dev->priv`. PM hooks delegate to `ssb_bus_suspend/resume`.

## State and Persistence
State is the allocated `struct ssb_bus` stored in `pcmcia_device->priv` and the active PCMCIA window/device configuration. No persistent storage is touched.

## Dependencies and Integration Points
Depends on PCMCIA core, CIS IDs, SSB PCMCIA host registration, and SSB bus suspend/resume.

## Risks
The probe uses legacy PCMCIA resource window semantics; incorrect window flags, missing IRQ, or failed map/enable prevents bus registration. Suspend/resume assumes `dev->priv` remains valid.

## Test Signals
Matching cards should register an SSB bus and devices; failure logs include both PCMCIA result and SSB error. Suspend/resume should preserve SSB operation and cleanup should release the window without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/bridge_pcmcia_80211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/driver_chipcommon.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/driver_chipcommon.c

## Purpose
Driver for the Broadcom SSB ChipCommon core, covering clock/power setup, PMU handoff, watchdog access, flash/external bus timings, GPIO register helpers, IRQ status/mask helpers, and optional UART discovery.

## Important APIs, Types, and Functions
Public functions include `ssb_chipcommon_init/suspend/resume`, `ssb_chipco_set_clockmode`, clock getters, timing init, watchdog setters, IRQ helpers, GPIO helpers (`ssb_chipco_gpio_*`), and optional `ssb_chipco_serial_init`. Internal helpers derive slow clock source/frequency limits, power-control delays, watchdog limits, and masked register writes under `gpio_lock`.

## Control Flow
Init validates ChipCommon presence, initializes GPIO lock, reads status for rev >=11, clears pullup/pulldown for rev >=20, initializes PMU if present, sets power-control timing, forces fast clock mode, calculates PCI fast powerup delay, and computes watchdog timing for SoC buses. Suspend sets slow clock mode; resume re-runs power control and fast mode. GPIO helpers perform masked read-modify-write with spinlocks. Serial init chooses baud source based on PLL type/revision, optionally toggles UART clocks, and fills port descriptors.

## State and Persistence
Updates `struct ssb_chipcommon` fields such as `status`, `fast_pwrup_delay`, `ticks_per_ms`, and `max_timer_ms`. Hardware state persists in ChipCommon clock, GPIO, watchdog, PMU, and timing registers.

## Dependencies and Integration Points
Used by SSB main bus power management, MIPS core flash/serial setup, GPIO driver, embedded watchdog registration, PMU code, and PCI xtal control. Depends on `ssb_read/write`, PCI config access for old clock source detection, and BCM47xx watchdog definitions.

## Risks
Clock mode handling is revision-sensitive and PMU-capable chips bypass legacy control. Wrong timing calculations can break flash, UART, or external I/O. Watchdog width differs by revision/PMU and clamps requested ticks. GPIO RMW must stay locked to avoid lost updates.

## Test Signals
Boot logs should show ChipCommon status and PMU detection where present. Validate clock speed, UART baud, watchdog max, GPIO direction/value/pull behavior, and suspend/resume without losing bus access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/driver_chipcommon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/driver_chipcommon_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/driver_chipcommon_pmu.c

## Purpose
Power Management Unit support for ChipCommon: programs PLLs, resource masks/dependencies, LDO voltages, PA reference LDO, ALP/CPU/control clocks, and spur-avoidance PLL updates for selected Broadcom chips.

## Important APIs, Types, and Functions
Core entry is `ssb_pmu_init`; exports `ssb_pmu_set_ldo_voltage`, `ssb_pmu_set_ldo_paref`, `ssb_pmu_get_alp_clock`, `ssb_pmu_get_cpu_clock`, `ssb_pmu_get_controlclock`, and `ssb_pmu_spuravoid_pllupdate`. Internal tables describe PMU0/PMU1 crystal PLL settings and per-chip resource up/down/dependency changes.

## Control Flow
`ssb_pmu_init` checks PMU capability, reads PMU revision, sets `NOILPONW` according to revision, then calls PLL and resource init. PLL init optionally reads `xtalfreq` from BCM47xx NVRAM for SoC buses, selects a per-chip PLL routine, powers PLL resources down, waits for HT to clear, writes PLL control registers, and writes crystal/divider fields. Resource init selects min/max masks and table updates by chip ID, writes resource rows, applies dependencies, and sets min/max masks. LDO and spur functions write register-control or PLL-control fields for supported chips.

## State and Persistence
Stores `cc->pmu.rev` and `cc->pmu.crystalfreq`; most effects persist in PMU PLL, resource, and regulator registers until reset or later reprogramming.

## Dependencies and Integration Points
Called by ChipCommon init and used by ChipCommon clock/watchdog logic. Depends on ChipCommon register accessors, delays, Broadcom NVRAM on BCM47xx, and chip ID/revision definitions.

## Risks
Unsupported chip IDs mostly log errors and keep defaults, which may be acceptable or may leave clocks/resources wrong. PLL programming has hardware sequencing delays and can fail if HT does not drop. `BUG_ON` in clock-table lookups assumes register values map to known tables. LDO/spur functions silently no-op for unsupported chips.

## Test Signals
On supported chips, logs should show PMU revision and PLL programming only when needed. Validate ALP/control/CPU clock values, resource masks, wireless stability after spur-avoidance changes, and no HT-off timeout emergency messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/driver_chipcommon_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/driver_chipcommon_sflash.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/driver_chipcommon_sflash.c

## Purpose
Serial flash detection for ChipCommon-backed SSB systems, preparing a platform device exposing flash memory metadata to the MTD stack.

## Important APIs, Types, and Functions
Defines `ssb_sflash_dev`, `ssb_sflash_resource`, flash ID tables for ST/SST/Atmel parts, internal `ssb_sflash_cmd`, and public `ssb_sflash_init`.

## Control Flow
Init switches on ChipCommon flash type. ST/SST probing issues deep-powerdown/release commands and reads IDs at flash addresses 0/1; Atmel probing reads status ID. It searches the corresponding table, fills `bus->mipscore.sflash` window/block/size/present fields, adjusts the platform resource end, and attaches platform data. The platform device is prepared but registered later by `main.c` after allocation services are ready.

## State and Persistence
Stores serial flash metadata in `struct ssb_sflash` and global platform device/resource fields. Hardware commands can affect flash power/read-ID state but do not modify flash contents.

## Dependencies and Integration Points
Called from `ssb_mips_flash_detect`, consumed by SSB device registration and MTD platform handling. Uses ChipCommon flash control/address/data registers.

## Risks
Unsupported IDs return `-ENOTSUPP`, preventing serial flash platform registration. Command polling is fixed at 1000 iterations with no sleep, so slow hardware may timeout. Global platform device/resource means multiple independent SSB serial flash instances would be problematic.

## Test Signals
Logs should identify flash name, size, block size, and count. MTD registration should see `ssb_sflash` with correct window and resource size; unsupported devices should fail without corrupting flash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/driver_chipcommon_sflash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/driver_extif.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/driver_extif.c

## Purpose
Driver helpers for the SSB EXTIF core, providing external interface timing setup, optional external UART discovery, watchdog control, clock-control reads, and GPIO helpers.

## Important APIs, Types, and Functions
Important functions are `ssb_extif_init`, `ssb_extif_timing_init`, `ssb_extif_get_clockcontrol`, watchdog setters, GPIO helpers (`ssb_extif_gpio_*`), and optional `ssb_extif_serial_init`. Internal helpers wrap `ssb_read/write` and masked RMW.

## Control Flow
Init creates the EXTIF GPIO lock when an EXTIF device exists. Timing init enables programmable interface access and programs flash/UART wait counts from a supplied bus-cycle nanosecond value. Serial init disables GPIO interrupts, probes up to two UART windows at `SSB_EUART` with loopback modem-control checks, and fills port descriptors. GPIO and watchdog helpers perform direct register or locked masked updates.

## State and Persistence
State lives in EXTIF hardware registers and `extif->gpio_lock`. Watchdog/timing/GPIO settings persist until reset or overwritten.

## Dependencies and Integration Points
Used by MIPS core initialization, embedded watchdog/GPIO APIs, GPIO driver, and clock calculations. Depends on serial core constants, ioremap/iounmap for UART probing, and SSB register accessors.

## Risks
UART probing maps and unmaps a small fixed physical region and assumes legacy register layout. Timing values depend on correct bus clock. GPIO interrupt support is elsewhere and assumes polarity toggling semantics.

## Test Signals
Validate detected UART count/baud/IRQ, EXTIF watchdog programming, GPIO direction/value/interrupt mask behavior, and stable flash/external UART access after timing init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/driver_extif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/driver_gige.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/driver_gige.c

## Purpose
Built-in driver for the SSB Gigabit Ethernet core that exposes the core as a pseudo PCI controller/device so standard PCI-oriented Ethernet plumbing can bind and receive fixed resources/IRQ routing.

## Important APIs, Types, and Functions
Defines SSB ID table for `SSB_DEV_ETHERNET_GBIT`, SSB driver `ssb_gige_driver`, PCI config-space read/write ops, `ssb_gige_probe`, `pdev_is_ssb_gige_core`, `ssb_gige_pcibios_plat_dev_init`, `ssb_gige_map_irq`, `ssb_gige_init`, and `ssb_gige_exit`.

## Control Flow
Probe allocates `struct ssb_gige`, initializes PCI controller/resources/ops, enables the SSB device, derives BAR0 base from `SSB_ADMATCH1`, writes emulated PCI BAR/command registers, configures write flushing, adjusts GMII/RGMII TMSLOW bits, stores driver data, and registers the PCI controller. Platform PCI fixups later match the pseudo bus ops, overwrite PCI resource 0, and assign IRQ `ssb_mips_irq(sdev)+2`.

## State and Persistence
Runtime state is allocated `struct ssb_gige` with spinlock, PCI ops/controller, resources, and `has_rgmii`. Hardware state includes PCI config shadow registers, shim flush control, and TMSLOW DLL/bypass bits.

## Dependencies and Integration Points
Integrates with SSB driver core, MIPS PCI controller registration, embedded PCI BIOS callbacks, `ssb_admatch_base`, and Linux PCI resource/IRQ setup.

## Risks
Only slot/function zero is emulated. Resource naming is used by `pdev_is_ssb_gige_core`, so changes can break detection. IRQ is hard-coded relative to MIPS IRQ assignment. Flush behavior notes that IRQ handlers must manually flush writes.

## Test Signals
GigE core should register a PCI controller, expose fixed BAR0 and IRQ, select RGMII/GMII path correctly, and allow the Ethernet PCI driver to probe. Config-space accesses outside function zero should return device-not-found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/driver_gige.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/driver_gpio.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/driver_gpio.c

## Purpose
GPIO provider for SSB systems, exposing ChipCommon or EXTIF GPIO registers through gpiolib and, on embedded SSB buses, mapping GPIO lines to Linux IRQs.

## Important APIs, Types, and Functions
Public functions are `ssb_gpio_init` and `ssb_gpio_unregister`. Backend functions implement gpiolib callbacks for get/set/direction/request/free for ChipCommon and get/set/direction for EXTIF. Embedded builds add `ssb_gpio_to_irq`, irq chips, IRQ handlers, domain init/exit for both backends.

## Control Flow
`ssb_gpio_init` prefers ChipCommon when available, otherwise EXTIF. Backend init fills `bus->gpio`, sets deterministic base 0 for SoC SSB buses or dynamic base for others, initializes IRQ domain if embedded, then registers with `gpiochip_add_data`. IRQ handlers compute pending lines from `(GPIOIN ^ polarity) & mask`, dispatch each line through the irqdomain, then update polarity to current values for edge-like behavior. Unregister removes the gpiochip; domain exit runs on init failure paths.

## State and Persistence
State is `bus->gpio`, optional `bus->irq_domain`, and backend hardware GPIO output, enable, pull, polarity, and interrupt mask registers. ChipCommon request/free also changes pull-up/down state.

## Dependencies and Integration Points
Depends on gpiolib, irqdomain, generic IRQ handling, SSB ChipCommon/EXTIF helpers, and `ssb_mips_irq` for parent interrupt selection.

## Risks
The unregister path removes only the gpiochip and does not explicitly call backend IRQ domain exit, so teardown depends on gpiolib/lifetime expectations. `free_irq` passes `chipco`/`extif` while `request_irq` used `bus` as `dev_id`, which looks suspicious for shared IRQ removal. IRQ polarity-toggling must be correct or edges can be lost/repeated.

## Test Signals
GPIO chip appears with 16 ChipCommon or 5 EXTIF lines, direction/value operations update hardware, `to_irq` works only for SoC SSB buses, GPIO IRQs dispatch through the domain, and module/bus removal does not leave IRQ mappings behind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/driver_gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/driver_mipscore.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/driver_mipscore.c

## Purpose
MIPS core support for SSB SoCs: assigns backplane IRQ routing, initializes serial ports, detects flash, sets external timing, computes CPU clock, and prepares platform flash devices/NVRAM discovery.

## Important APIs, Types, and Functions
Public functions include `ssb_mips_irq`, `ssb_cpu_clock`, and `ssb_mipscore_init`. Key internals are `ssb_irqflag`, `find_device`, `clear_irq`, `set_irq`, `dump_irq`, `ssb_mips_serial_init`, and `ssb_mips_flash_detect`. Defines global `ssb_pflash_dev` and resource/data for physmap flash.

## Control Flow
Init returns if no MIPS core exists. It computes bus clock and nanoseconds, initializes EXTIF or ChipCommon timings, iterates all SSB devices assigning IRQs based on core type and available MIPS interrupt lines, dumps routing, initializes serial ports via EXTIF/ChipCommon, and detects serial or parallel flash. Flash detection uses ChipCommon flash capability if present, otherwise assumes a default 4 MiB parallel flash window; it also seeds BCM47xx NVRAM from detected flash memory.

## State and Persistence
Updates `dev->irq` for each SSB device, `mcore->nr_serial_ports`, serial descriptors, `mcore->sflash`/`pflash`, global flash platform resources, MIPS core IPSFLAG/INTVEC registers, and flash timing registers.

## Dependencies and Integration Points
Used by SSB bus registration before device attach. Integrates with ChipCommon/EXTIF timing and serial helpers, serial core descriptors, MTD physmap, BCM47xx NVRAM, and SSB sflash init.

## Risks
IRQ routing manipulates shared MIPS core registers and may reassign old devices recursively. Some return values encode disabled/unassigned/not-supported IRQs as 5/0/6, which callers must interpret correctly. Flash defaults can be wrong on unusual boards without ChipCommon. Global flash device/resource limits multi-bus scenarios.

## Test Signals
After init, debug IRQ dump should match expected core routing, serial ports should register with correct baud/IRQ, NVRAM should initialize from correct flash window, and MTD platform devices should reflect flash size and bus width.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/driver_mipscore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/driver_pcicore.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/driver_pcicore.c

## Purpose
PCI/PCIe core support for SSB, including optional MIPS host-mode external PCI controller setup, client-mode PCI/PCIe workarounds, MDIO/SerDes programming, and interrupt-vector enablement for SSB devices behind PCI hosts.

## Important APIs, Types, and Functions
Public functions are `ssb_pcicore_init`, `ssb_pcicore_dev_irqvecs_enable`, and, in hostmode builds, `ssb_pcicore_plat_dev_init` and `ssb_pcicore_pcibios_map_irq`. Hostmode internals implement PCI config-space ops through `get_cfgspace_addr`, `ssb_extpci_read_config`, `ssb_extpci_write_config`, and `ssb_pcicore_init_hostmode`. Workarounds include SPROM core-index fix, PCI/PCIe setup, SerDes polarity, and MDIO read/write.

## Control Flow
`ssb_pcicore_init` enables the core, detects host mode on supported BCM47xx/BCM53xx SoCs without `NOPCI`, and either initializes external PCI host mode or client mode. Host mode resets the external bus, configures SSB-to-PCI windows, waits for devices, enables bridge memory/mastering/interrupts, maps I/O, and registers a PCI controller. Client mode fixes SPROM core index for PCI-hosted SSB, disables PCI interrupts, and applies PCIe SerDes workarounds. IRQ-vector enabling routes device interrupts through PCI config mask or SSB INTVEC depending on core revision/type, then runs setup workarounds once.

## State and Persistence
State includes `pc->hostmode`, `pc->cardbusmode`, `pc->setup_done`, global `extpci_core`, global config lock, and hardware bridge/window/MDIO/TMSLOW/SPROM registers. Hostmode registers a global PCI controller.

## Dependencies and Integration Points
Depends on SSB core accessors, Linux PCI subsystem, MIPS `get_dbe` bus probing, embedded GPIO for CardBus reset, `ssb_mips_irq`, and `ssb_commit_settings`.

## Risks
Host mode is MIPS-specific and only supports one external PCI core through global `extpci_core`. Config-space access remaps physical addresses per access and relies on bus exception probing. Timing delays after reset are hardware-critical. Workarounds are revision-specific and incomplete for some TODO cases such as ASPM and power thresholds.

## Test Signals
Client mode should enable IRQ routing and apply PCI/PCIe workarounds once. Host mode should enumerate external PCI devices without machine checks, assign IRQs, set bridge latency/BAR controls, and survive CardBus reset paths. MDIO transactions should complete within retry bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/driver_pcicore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/embedded.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/embedded.c

## Purpose
Embedded SSB glue exposing watchdog/GPIO convenience APIs and PCI BIOS callbacks that route PCI platform initialization and IRQ mapping to SSB PCI core or GigE pseudo-PCI devices.

## Important APIs, Types, and Functions
Exports `ssb_watchdog_timer_set`, GPIO helpers (`ssb_gpio_in/out/outen/control/intmask/polarity`), and implements `ssb_watchdog_register`, `ssb_pcibios_plat_dev_init`, and `ssb_pcibios_map_irq`. GigE callback helpers search registered buses for active GigE cores.

## Control Flow
Watchdog registration picks ChipCommon or EXTIF backend, fills a `bcm47xx_wdt` descriptor, and registers a `bcm47xx-wdt` platform device. GPIO helpers lock `bus->gpio_lock`, dispatch to ChipCommon or EXTIF backend, and return the masked result. PCI BIOS init first tries PCI core handling, then optional GigE callbacks via `ssb_for_each_bus_call`. IRQ mapping follows the same order.

## State and Persistence
Stores `bus->watchdog` platform device and changes backend watchdog/GPIO registers. PCI callbacks do not store new state except through downstream PCI resource and IRQ fixups.

## Dependencies and Integration Points
Requires embedded SSB, BCM47xx watchdog interface, platform devices, SSB PCI core, optional GigE driver, and global SSB bus list iteration.

## Risks
GPIO helpers warn but otherwise return zero when no backend exists. Watchdog registration assumes max timer fields were initialized by ChipCommon/EXTIF. PCI BIOS callbacks depend on SSB buses and built-in core drivers already being registered.

## Test Signals
On BCM47xx SoCs, watchdog platform device should register and set timers through correct backend. GPIO exported helpers should be serialized and reflect hardware. PCI devices behind SSB PCI/GigE should receive fixed resources and IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/embedded.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/host_soc.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/host_soc.c

## Purpose
Host operations for memory-mapped SoC SSB buses with no external PCI/PCMCIA/SDIO host, plus invariant extraction from BCM47xx NVRAM and SPROM fallback.

## Important APIs, Types, and Functions
Defines `ssb_host_soc_ops` with byte/word/dword read/write and optional block I/O callbacks. Public `ssb_host_soc_get_invariants` fills `struct ssb_init_invariants` from NVRAM and fallback SPROM.

## Control Flow
Read/write ops compute `bus->mmio + core_index * SSB_CORE_SIZE + offset` and perform direct MMIO accesses. Block I/O loops over the same fixed address using raw accessors at the requested width. Invariant extraction reads `boardvendor`, `boardtype`, and `cardbus` NVRAM variables, defaults vendor to Broadcom when absent, and calls `ssb_fill_sprom_with_fallback`.

## State and Persistence
No private state beyond values written to caller-provided invariants. Hardware MMIO writes directly affect SSB core registers. Parsed board info persists in `struct ssb_bus` after main registration copies it.

## Dependencies and Integration Points
Used by `ssb_bus_host_soc_register` in `main.c`. Depends on BCM47xx NVRAM and SSB fallback SPROM infrastructure.

## Risks
Block I/O warns on unaligned byte counts but still loops by width. Invalid NVRAM values only warn and may leave board fields zero/default. Direct SoC mapping assumes `bus->mmio` covers all cores at `SSB_CORE_SIZE` strides.

## Test Signals
SoC bus registration should scan cores through these ops, board vendor/type should match NVRAM or defaults, fallback SPROM should populate wireless data, and block I/O should match scalar reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/host_soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/main.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/main.c

## Purpose
Central SSB bus core: registers the `ssb` bus type, manages global bus lists and early-boot attach queue, registers SSB devices/drivers, handles bus power/suspend/resume, initializes built-in cores, calculates clocks/DMA translation, and wires optional bridge drivers at module init/exit.

## Important APIs, Types, and Functions
Exports bus lookup/iteration (`ssb_pci_dev_to_bus`, `ssb_pcmcia_dev_to_bus`, `ssb_for_each_bus_call`), power (`ssb_bus_powerup`, `ssb_bus_may_powerdown`, suspend/resume), registration APIs for PCI/PCMCIA/SDIO/SoC hosts, driver registration, `ssb_set_devtypedata`, `ssb_calc_clock_rate`, `ssb_clockspeed`, device enable/disable/is-enabled, `ssb_dma_translation`, `ssb_commit_settings`, `ssb_admatch_base`, and `ssb_admatch_size`.

## Control Flow
Host-specific register functions set bus type/ops and call `ssb_bus_register`. Registration powers xtal/PLL, initializes host transport, locks global lists, scans cores, initializes PCI/PCMCIA support, powers the bus, initializes ChipCommon/EXTIF/MIPS core, fetches invariants, queues the bus, and attaches immediately after early boot. Attach powers up, initializes PCI core, registers watchdog/GPIO, powers down if allowed, registers non-system SSB devices, and moves the bus to the live list. Device registration skips system cores handled internally, creates wrapper devices for functional cores, sets parent/DMA/IRQ based on host type, and registers flash platform devices if detected. `fs_initcall` registers the bus type, drains early queue, and initializes b43 PCI bridge, PCMCIA host, and GigE driver.

## State and Persistence
Global state includes `attach_queue`, live `buses`, `next_busnumber`, `buses_mutex`, and `ssb_is_early_boot`. Per-bus state includes mapped device, power flags, core arrays, board/SPROM data, device wrappers, GPIO/watchdog/flash state, and host pointers. Hardware state includes TMSLOW/TMSHIGH/IMSTATE, clock/xtal registers, and broadcast settings.

## Dependencies and Integration Points
Integrates all SSB host backends, scan/sprom helpers, ChipCommon/PMU/EXTIF/MIPS/PCI/GigE/GPIO code, Linux driver core, platform devices, DMA mapping, PCI, PCMCIA, SDIO, and module/initcall ordering.

## Risks
Early-boot queue locking is conditional, so ordering is delicate. Error unwinding spans multiple subsystems and must keep list/mapping/power state consistent. System cores are not registered as regular devices, so built-in init must stay complete. Device enable/disable sequences include timing and reject-bit differences by backplane revision; mistakes can cause machine checks. DMA translation has chip-specific exceptions.

## Test Signals
Exercise early SoC registration and late hotplug-like host registration, verify core scan and functional device creation, suspend/resume reinitializes power and PCI setup, unregister removes devices/GPIO/mappings, clock calculations match hardware, and b43/PCMCIA/GigE init failures remain non-fatal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/pci.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/pci.c

## Purpose
PCI-host backend for SSB: manages BAR0 core window switching, PCI xtal/PLL control, SPROM reading/writing/parsing, board invariant extraction, PCI MMIO access ops, and a sysfs SPROM attribute.

## Important APIs, Types, and Functions
Public functions include `ssb_pci_switch_coreidx`, `ssb_pci_switch_core`, `ssb_pci_xtal`, `ssb_pci_get_invariants`, `ssb_pci_init`, `ssb_pci_exit`, and `ssb_pci_ops`. SPROM helpers include CRC calculation/checking, read/write, revision-specific extraction (`sprom_extract_r123`, `r45`, `r8`), fallback handling, and sysfs show/store callbacks.

## Control Flow
Core switching writes `SSB_BAR0_WIN`, reads it back until the requested core index is mapped, and updates `bus->mapped_device` under `bar_lock`. `ssb_pci_xtal` toggles PCI GPIO output/enable bits for XTAL/PLL and clears target-abort status on power-up. SPROM get selects offset based on ChipCommon revision/status, tries legacy and rev4+ sizes with CRC, falls back to platform SPROM when both fail, then extracts fields by revision. MMIO ops assert the bus is powered, switch core if needed, then perform ioread/iowrite or block I/O. Init creates an admin RW `ssb_sprom` file on the host PCI device.

## State and Persistence
State includes `bus->mapped_device`, `sprom_mutex`, `sprom_offset`, `sprom_size`, parsed `bus->sprom`, board info, power warning count, and hardware PCI GPIO/BAR/window/SPROM contents. `sprom_do_write` persistently writes SPROM and must not be interrupted.

## Dependencies and Integration Points
Used by SSB main registration for PCI buses, SPROM invariants, and `ssb_pci_ops`. Depends on Linux PCI config access, MMIO, SPROM fallback infrastructure, sysfs device attributes, and `ssb_pci_dev_to_bus`.

## Risks
BAR window switching failures break all core access. MMIO while powered down logs fatal errors and returns all-ones values, so callers may misinterpret absent hardware. SPROM write is slow and persistent; bad CRC validation or interrupted power can brick calibration data. Unsupported SPROM revisions fall back to v1 extraction, risking incomplete wireless calibration.

## Test Signals
Validate core switching under concurrent access, xtal/PLL power transitions, SPROM sysfs read/write CRC enforcement, fallback SPROM path, parsed board/mac/power fields for revisions 1/2/3/4/5/8, and powered-down access warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/pci.c -->
