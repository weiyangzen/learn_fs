# Research: subset-b-001071

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mvebu-mbus.c -->
# sources/distributed-fs/ceph-client/drivers/bus/mvebu-mbus.c

## Purpose
This driver manages Marvell EBU MBus address decode windows for Kirkwood, Armada 370/XP/375/380, Dove, Orion5x, and MV78xx0 SoCs. It reads SDRAM decode windows, exposes DRAM target information to other Marvell device drivers for DMA setup, allocates/removes CPU-to-device windows, records optional PCIe apertures from device tree, and provides debugfs visibility under `mvebu-mbus`.

## Important APIs, Types, and Functions
The central state is `struct mvebu_mbus_state`, which holds mapped register bases, SoC layout callbacks, PCIe aperture resources, debugfs dentries, coherency state, and suspend snapshots. `struct mvebu_mbus_soc_data` abstracts per-SoC window counts, register offsets, remap capability, SDRAM decode parsing, debug display, and save routines. Exported integration APIs include `mv_mbus_dram_info()`, `mv_mbus_dram_info_nooverlap()`, `mvebu_mbus_add_window_by_id()`, `mvebu_mbus_add_window_remap_by_id()`, `mvebu_mbus_del_window()`, `mvebu_mbus_get_pcie_mem_aperture()`, `mvebu_mbus_get_pcie_io_aperture()`, `mvebu_mbus_get_dram_win_info()`, and `mvebu_mbus_get_io_win_info()`.

## Control Flow
Initialization is either board-file driven through `mvebu_mbus_init()` or device-tree driven through `mvebu_mbus_dt_init()`. The DT path finds a matching MBus node, resolves the `controller` phandle, maps CPU-window and SDRAM-window resources, optionally maps the MBus bridge for suspend/resume, reads PCIe aperture properties, disables all existing CPU windows, builds DRAM target tables, enables sync-barrier support when coherent, and finally installs static windows from `ranges`. Window creation validates power-of-two size, base alignment, overlap exclusion, and remap capability before writing base/control/remap registers.

## State and Persistence
State is process-global in `mbus_state`, which is expected because MBus is a singleton SoC fabric. Hardware programming persists in MMIO registers. Suspend stores all CPU decode windows plus optional bridge registers in `mbus_state.wins`, `mbus_bridge_ctrl`, and `mbus_bridge_base`; resume restores them through registered syscore ops. Debugfs files read live registers rather than cached state.

## Dependencies and Integration Points
The driver depends on early Linux init, OF address parsing, `memblock`, `debugfs`, `syscore`, `ioremap`, and `linux/mbus.h` consumers. It is a prerequisite for platform devices needing MBus windows or device-to-DRAM DMA attributes. Static windows are derived from DT `ranges`; PCIe integration uses optional `pcie-mem-aperture` and `pcie-io-aperture`.

## Risks and Test Signals
The main risks are incorrect DT ranges, overlapping or non-power-of-two windows, missing bridge resources that break suspend/resume, and singleton global state being used before initialization. Useful signals are boot logs for window allocation errors, debugfs `mvebu-mbus/sdram` and `devices` contents, PCIe/resource probing, DMA correctness for Marvell devices, and suspend/resume on bridge-capable Armada SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/mvebu-mbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/omap-ocp2scp.c -->
# sources/distributed-fs/ceph-client/drivers/bus/omap-ocp2scp.c

## Purpose
This small platform bus driver enables TI OMAP OCP-to-SCP bridge nodes, populates their child devices, and applies a hardware timing workaround for non-AM437x variants. The bridge translates OCP accesses to SCP protocol for child PHY-like devices.

## Important APIs, Types, and Functions
`omap_ocp2scp_probe()` is the only substantive path. It calls `of_platform_populate()` for children, enables runtime PM on the bridge, maps the first MMIO resource when the timing workaround applies, and writes the `OCP2SCP_TIMING` register `SYNC2` field to `0x6`. `omap_ocp2scp_remove()` disables runtime PM and depopulates children. The OF match table recognizes `ti,omap-ocp2scp` and `ti,am437x-ocp2scp`.

## Control Flow
Probe first populates child resources from the bridge node. After `pm_runtime_enable()`, non-AM437x hardware gets a runtime PM get, a read-modify-write of `OCP2SCP_TIMING`, and a runtime PM put. Error unwinding disables runtime PM and depopulates children if mapping fails. AM437x skips the timing write entirely.

## State and Persistence
The driver has no private state. The only persistent hardware change is the `SYNC2` timing field, which remains programmed until reset or power-domain loss. Runtime PM state is owned by the core.

## Dependencies and Integration Points
It depends on OF child population, platform resources, MMIO accessors, and runtime PM. Its main integration point is child platform devices that sit behind the OCP2SCP bridge.

## Risks and Test Signals
The main risk is ordering: children are populated before the timing workaround, so early child access would depend on probe ordering and PM behavior. Missing MMIO resources on non-AM437x devices fail probe. Test signals include successful child device probing, absence of read-path errors on OMAP4/5/AM57xx, and runtime PM balance during probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/omap-ocp2scp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/omap_l3_noc.c -->
# sources/distributed-fs/ceph-client/drivers/bus/omap_l3_noc.c

## Purpose
This is the OMAP4/OMAP5/DRA7/AM437x L3 NOC error handler. It decodes interconnect application/debug faults, identifies the target and master from register tables, emits detailed warnings, clears handled errors, and masks undocumented un-clearable sources to avoid interrupt storms.

## Important APIs, Types, and Functions
The runtime object is `struct omap_l3` from `omap_l3_noc.h`. `omap_l3_probe()` copies SoC-specific static data, maps each L3 module, and requests debug and application IRQs. `l3_interrupt_handler()` locates the active flagmux bit and delegates to `l3_handle_target()`. `l3_handle_target()` reads target stderrlog registers, distinguishes standard versus custom errors, decodes master ID, opcode, request mode, target name, and clears the log with `CLEAR_STDERR_LOG`. `l3_resume_noirq()` reapplies software masks for ignored bits after suspend.

## Control Flow
At `postcore_initcall_sync`, the platform driver registers early enough to catch bus faults. Probe maps module resources, respecting `L3_BASE_IS_SUBMODULE` aliases, then requests two hard IRQ handlers with `IRQF_NO_THREAD`. On IRQ, the handler selects application or debug registers from the IRQ number, masks already ignored bits, handles the first set error bit, and returns immediately after one source. Unknown targets are logged, masked in hardware, and recorded in `mask_app_bits` or `mask_dbg_bits`.

## State and Persistence
SoC tables are static, but probe copies the matched `struct omap_l3` into device-managed memory and mutates runtime bases, IRQ numbers, and ignore masks. The masks persist in memory and are restored to hardware after noirq resume.

## Dependencies and Integration Points
The driver depends on OF matching, platform IRQ/resource descriptions, MMIO, and the SoC tables in `omap_l3_noc.h`. It integrates with kernel diagnostics through `WARN()` and with PM through noirq resume.

## Risks and Test Signals
Risks include table/register offset drift, `BUG_ON()` for out-of-range target indexes, only handling the first pending source per IRQ, and masking real faults if an undocumented bit appears. Test signals are decoded L3 warning messages for injected illegal accesses, no interrupt storm after boot-time stale bits, correct noirq resume mask restoration, and successful probing on each compatible SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/omap_l3_noc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/omap_l3_noc.h -->
# sources/distributed-fs/ceph-client/drivers/bus/omap_l3_noc.h

## Purpose
This header is the data model and SoC decode database for the OMAP L3 NOC error handler. It defines register offsets, status constants, core structs, transaction strings, target tables, master tables, flagmux layouts, and matched `struct omap_l3` templates for OMAP4, OMAP5, DRA7, and AM4372.

## Important APIs, Types, and Functions
Key types are `struct l3_masters_data`, `struct l3_target_data`, `struct l3_flagmux_data`, and `struct omap_l3`. Constants such as `L3_TARG_STDERRLOG_*`, `L3_FLAGMUX_REGERR0`, `L3_FLAGMUX_MASK0`, `CUSTOM_ERROR`, and `CLEAR_STDERR_LOG` define the register contract consumed by `omap_l3_noc.c`. `l3_transaction_type[]` maps opcodes to printable transaction classes.

## Control Flow
There is no executable control flow beyond static initialization. Probe in the C file selects one of the static `omap*_l3_data` templates through OF match data, then interrupt handling uses the selected pointer graph to translate flagmux bit indexes into target offsets and names.

## State and Persistence
Most tables are static mutable objects, not `const`, because runtime code stores ignore masks in `struct l3_flagmux_data`. The matched `struct omap_l3` template itself is copied at probe time, but its nested `l3_flagmux` pointers still reference these static flagmux records, so mask state is shared per driver image.

## Dependencies and Integration Points
The header depends on kernel macros such as `ARRAY_SIZE`, `BIT`, and I/O types supplied by includers. It is tightly coupled to OMAP L3 register manuals and to the implementation in `omap_l3_noc.c`.

## Risks and Test Signals
The risk is correctness of static data: bad target offsets, duplicate or placeholder master IDs, mismatched `mst_addr_mask`, or unsupported targets can make diagnostics misleading or cause a source to be masked. Test signals are accurate decoded master/target names on each compatible SoC and no out-of-bounds target handling during L3 fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/omap_l3_noc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/omap_l3_smx.c -->
# sources/distributed-fs/ceph-client/drivers/bus/omap_l3_smx.c

## Purpose
This is the OMAP3 L3 SMX interconnect error handler. It catches application/debug L3 interrupts, decodes 64-bit error logs into error code, initiator, command, and address information, reports severe bus faults, clears agent/error registers, and intentionally BUGs on timeout-class application errors.

## Important APIs, Types, and Functions
`omap3_l3_probe()` allocates `struct omap3_l3`, maps the single L3 MMIO resource, and requests debug/application IRQs. `omap3_l3_app_irq()` handles both IRQ types by choosing status register 0 or 1, using the first set bit to index `omap3_l3_bases`, reading `L3_ERROR_LOG` and `L3_ERROR_LOG_ADDR`, calling `omap3_l3_block_irq()`, and clearing status/log registers. Inline decode helpers extract code, address, command, initiator ID, and request info.

## Control Flow
The driver registers at `postcore_initcall_sync`. Probe uses non-devm allocation and manual unwind for IRQ and ioremap resources. On interrupt, the handler reads a 64-bit status word, finds the first set source with `__ffs`, derives the target block base from static arrays in the header, logs the decoded error, BUGs if application status includes `L3_STATUS_0_TIMEOUT_MASK`, clears IA/TA status, and writes the error log value back.

## State and Persistence
Runtime state is limited to mapped base and IRQ numbers in `struct omap3_l3`. The hardware error log is transient and cleared by the IRQ handler. There is no suspend/resume state or debugfs state.

## Dependencies and Integration Points
The driver depends on `omap_l3_smx.h` for register definitions and source-to-block maps, platform IRQ/resource setup, raw 64-bit MMIO access macros, and OF matching when built with OF. It integrates with platform diagnostics through `pr_err`, `WARN_ON`, and `BUG_ON`.

## Risks and Test Signals
Risks include `__ffs(status)` on a zero status if a spurious IRQ arrives, zero offsets for reserved status bits, deliberate kernel panic on timeout errors, and non-devm lifetime complexity. Test signals are accurate decoded messages for OMAP3 L3 faults, correct clearing of error status, clean remove path, and expected panic behavior only for real timeout-class faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/omap_l3_smx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/omap_l3_smx.h -->
# sources/distributed-fs/ceph-client/drivers/bus/omap_l3_smx.h

## Purpose
This header defines the OMAP3 L3 SMX register contract, error status masks, initiator IDs, error code values, runtime state struct, and status-bit-to-agent-offset tables consumed by `omap_l3_smx.c`.

## Important APIs, Types, and Functions
Important constants include `L3_ERROR_LOG`, `L3_ERROR_LOG_ADDR`, sideband status registers, `L3_STATUS_0_TIMEOUT_MASK`, `L3_AGENT_STATUS_CLEAR_IA`, and `L3_AGENT_STATUS_CLEAR_TA`. `enum omap3_l3_initiator_id` and `enum omap3_l3_code` provide semantic decode values. `struct omap3_l3` stores the device pointer, optional clock pointer, L3 base, IRQs, and an `inband` bit. `omap3_l3_app_bases`, `omap3_l3_debug_bases`, and `omap3_l3_bases` map status bits to register-block offsets.

## Control Flow
The header has no active control flow, but its arrays directly drive interrupt routing: the IRQ handler indexes `omap3_l3_bases[int_type][err_source]` to find the agent block whose error log should be read and cleared.

## State and Persistence
The arrays and `shift` constant are static file-scope definitions emitted into each includer. The `struct omap3_l3` definition describes per-device runtime state, while hardware state remains in L3 registers.

## Dependencies and Integration Points
It depends on low-level I/O pointer checking for the local `__raw_readll`/`__raw_writell` macros and is tightly bound to OMAP3 TRM bit assignments. It is private to the OMAP3 SMX driver.

## Risks and Test Signals
The critical risk is stale or incomplete bit-to-offset mapping, especially because reserved entries are zero and can redirect decoding to the base block. The local raw 64-bit MMIO macros may also be architecture-sensitive. Test signals include matching decoded initiator names and addresses against hardware documentation and no false handling of reserved status bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/omap_l3_smx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/qcom-ebi2.c -->
# sources/distributed-fs/ceph-client/drivers/bus/qcom-ebi2.c

## Purpose
This driver configures Qualcomm EBI2/QPIC-era external memory bus chip-selects from device tree and then populates child devices attached to that parallel bus.

## Important APIs, Types, and Functions
`struct cs_data` maps chip-select indexes 0-5 to enable masks and slow/fast timing registers. `struct ebi2_xmem_prop` maps DT timing properties to register fields and maximum values. `qcom_ebi2_setup_chipselect()` enables a CS line, parses timing properties, caps out-of-range values, and writes slow/fast XMEMC registers. `qcom_ebi2_probe()` enables the `ebi2x` and `ebi2` clocks, maps the EBI2 and XMEM windows, disables all chip-selects, configures available children, and calls `of_platform_default_populate()`.

## Control Flow
Probe obtains and enables clocks before MMIO access. It writes `EBI2_XMEM_CFG` to disable power-save behavior, clears all CS enables, then walks each available child node. Each child must provide a `reg` chip-select index; invalid indexes are logged and skipped. If at least one child was configured, the driver populates child platform devices.

## State and Persistence
The driver keeps no private runtime state after probe. Persistent state is hardware register programming for enabled chip-selects and timing registers. Clocks are not explicitly disabled on successful remove because the driver has no remove callback in this source.

## Dependencies and Integration Points
It depends on CCF clocks, OF child nodes, platform resources, MMIO access, and DT bindings for `qcom,xmem-*` timing properties. It integrates with child memory/peripheral drivers by enabling their bus aperture before population.

## Risks and Test Signals
Risks include leaking enabled clocks for a module unload path, returning directly from missing child `reg` without disabling clocks, timing defaults of zero when properties are absent, and uncertain undocumented FAST register fields. Test signals are correct child probe, external memory read/write stability, clock enable errors on missing DT clocks, and register dumps matching expected timing values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/qcom-ebi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/qcom-ssc-block-bus.c -->
# sources/distributed-fs/ceph-client/drivers/bus/qcom-ssc-block-bus.c

## Purpose
This driver sequences clocks, resets, power domains, halt registers, and MPM always-on clamp overrides required to access the Qualcomm SSC block over AHB, then populates child devices inside the block.

## Important APIs, Types, and Functions
`struct qcom_ssc_block_bus_data` stores register pointers, halt regmap, clocks, resets, power-domain devices, and AXI halt offset. `qcom_ssc_block_bus_init()` performs the enable/deassert/unhalt sequence. `qcom_ssc_block_bus_deinit()` reverses it. Helper groups attach, enable, disable, and detach named power domains `ssc_cx` and `ssc_mx`.

## Control Flow
Probe maps named MPM config registers, gets two resets and six clocks, parses `qcom,halt-regs` into a syscon regmap plus offset, attaches and votes power domains to `INT_MAX`, initializes the bus, and populates child nodes. Error paths unwind power-domain attach/enable for early failures, while `qcom_ssc_block_bus_init()` has detailed internal unwind for clock/reset sequencing failures. Remove deinitializes the block, disables/detaches power domains, and calls PM cleanup helpers.

## State and Persistence
Runtime state is device-private and devm allocated. Hardware state includes clamp override bits, reset assertions, AXI halt request, and enabled clocks. Power-domain performance votes persist while the device is bound.

## Dependencies and Integration Points
The driver depends on named resources, reset framework, CCF clocks, generic power domains, runtime PM, syscon/regmap, and OF population. It is an enablement wrapper for SSC child devices.

## Risks and Test Signals
Risks include `qcom_ssc_block_bus_init()` return value being ignored in probe, use of `clk_disable()` instead of `clk_disable_unprepare()` in unwind/deinit despite prepare-enable calls, and manual sequencing fragility. Test signals include successful child probing after power collapse, AXI halt acknowledgement/idle behavior, no clock/reset imbalance warnings, and correct cleanup on deferred probe or remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/qcom-ssc-block-bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/simple-pm-bus.c -->
# sources/distributed-fs/ceph-client/drivers/bus/simple-pm-bus.c

## Purpose
This generic transparent bus driver adds runtime/system PM around simple DT bus nodes that need clocks enabled while their children are active. It also safely declines to manage pure `simple-bus`-style nodes when this driver is not the most specific binding.

## Important APIs, Types, and Functions
`struct simple_pm_bus` stores all clocks returned by `devm_clk_bulk_get_all()`. `simple_pm_bus_probe()` handles override and match specificity checks, allocates state, enables runtime PM, and populates children. Runtime PM callbacks use `clk_bulk_prepare_enable()` and `clk_bulk_disable_unprepare()`. System sleep callbacks force runtime PM suspend/resume when the bus is managed.

## Control Flow
Probe returns immediately for `driver_override` bindings. For `ONLY_BUS` match entries, probe only proceeds if that compatible is the first compatible string; otherwise it returns `-ENODEV` so a more specific driver can bind. Managed buses acquire all clocks, enable PM, and populate children using optional auxdata. Remove mirrors only PM disable because child devices are handled by platform core/devm lifetime.

## State and Persistence
The only runtime state is the clock bulk pointer/count. Clock state is controlled by runtime PM and restored through force suspend/resume. No hardware registers are programmed directly.

## Dependencies and Integration Points
It depends on OF matching/population, CCF bulk clock APIs, runtime PM, and platform devices. It is shared infrastructure for SoC buses with child devices but minimal bus-specific logic.

## Risks and Test Signals
Risks include accidentally binding to a node with a more specific driver if compatible ordering is wrong, leaving children populated after failed later work, and clock naming/availability problems. Test signals are child devices probing only under intended nodes, balanced runtime PM usage, clock enable/disable transitions during autosuspend, and no regression for plain `simple-bus` nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/simple-pm-bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/stm32_dbg_bus.c -->
# sources/distributed-fs/ceph-client/drivers/bus/stm32_dbg_bus.c

## Purpose
This STM32 debug bus driver exposes an OP-TEE mediated firewall controller that grants or denies debug-bus access based on secure firmware policy, then populates permitted debug-bus children.

## Important APIs, Types, and Functions
`struct stm32_dbg_bus` stores the TEE client device and OP-TEE context. `stm32_dbg_pta_open_session()` and `stm32_dbg_pta_close_session()` manage PTA sessions. `stm32_dbg_bus_grant_access()` invokes `PTA_CMD_GRANT_DBG_ACCESS` with either `PERIPHERAL_DBG_PROFILE` or `HDP_DBG_PROFILE`. `stm32_dbg_bus_plat_probe()` registers a `struct stm32_firewall_controller` and calls `stm32_firewall_populate_bus()`. Separate TEE and platform drivers are registered from one module init path.

## Control Flow
The TEE client probe opens an OP-TEE context and installs a singleton `stm32_dbg_bus_priv`. The platform probe defers until that singleton exists, then registers the firewall controller, filters children through the common STM32 firewall bus helper, enables runtime PM, and populates children. The TEE remove path closes the context and depopulates TEE children.

## State and Persistence
The singleton `stm32_dbg_bus_priv` enforces one debug bus instance. Access decisions are not cached by this driver; each grant opens a TEE session and invokes secure firmware. Release is a required no-op callback.

## Dependencies and Integration Points
It depends on OP-TEE client APIs, the STM32 firewall framework exported by `stm32_firewall.c`, OF platform population, and runtime PM. Its DT compatibles are STM32MP131 and STM32MP151 debug bus nodes, and its TEE service is identified by a fixed UUID.

## Risks and Test Signals
Risks include singleton ordering, context lifetime coupling between TEE and platform devices, missing unregister on some platform-probe failure paths, and secure firmware returning access denial. Test signals include deferred probe until OP-TEE is ready, expected `-EACCES` on forbidden profiles, children detached when access is denied, and no stale singleton after TEE remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/stm32_dbg_bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/stm32_etzpc.c -->
# sources/distributed-fs/ceph-client/drivers/bus/stm32_etzpc.c

## Purpose
This driver registers the STM32 ETZPC firewall controller and filters bus children based on ETZPC decode-protection settings. It covers peripheral and memory firewall entries.

## Important APIs, Types, and Functions
`stm32_etzpc_grant_access()` validates a firewall ID, reads the relevant `ETZPC_DECPROT` field, and permits access only when the peripheral is non-secure and attributed to Cortex-A7 (`ETZPC_PROT_A7NS`). `stm32_etzpc_probe()` maps ETZPC registers, fills `struct stm32_firewall_controller`, derives `max_entries` from `ETZPC_HWCFGR`, registers the controller, runs `stm32_firewall_populate_bus()`, and populates allowed children.

## Control Flow
Probe reads hardware configuration counts for secure peripherals and AHB masters, sets the max entry range, and registers with the shared STM32 firewall list. During bus population, each child’s `access-controllers` property is resolved and `stm32_etzpc_grant_access()` determines whether the node remains available for later platform population.

## State and Persistence
Private state is the devm-allocated firewall controller plus mapped MMIO. Hardware security configuration is read-only from this driver’s perspective. Release access is intentionally a no-op.

## Dependencies and Integration Points
It depends on the STM32 firewall framework, OF phandle parsing, platform MMIO resources, and ETZPC hardware configuration registers. It integrates with child platform devices by removing unauthorized nodes before `of_platform_populate()`.

## Risks and Test Signals
Risks include no unregister if `stm32_firewall_populate_bus()` fails after registration, access decisions depending entirely on bootloader/secure firmware configuration, and ID/count mismatches from DT. Test signals include correct `max_entries` from HWCFGR, denied nodes being detached, allowed child probes, and graceful `-EACCES` for secure-only peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/stm32_etzpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/stm32_firewall.c -->
# sources/distributed-fs/ceph-client/drivers/bus/stm32_firewall.c

## Purpose
This file implements the common STM32 firewall framework used by ETZPC, RIFSC, and debug-bus providers. It parses device-tree access-controller phandles, tracks registered firewall controllers, provides exported grant/release helpers for consumers, and filters bus children before platform population.

## Important APIs, Types, and Functions
Exported consumer APIs are `stm32_firewall_get_firewall()`, `stm32_firewall_grant_access()`, `stm32_firewall_grant_access_by_id()`, `stm32_firewall_release_access()`, `stm32_firewall_release_access_by_id()`, and `stm32_firewall_get_grant_all_access()`. Controller APIs are `stm32_firewall_controller_register()`, `stm32_firewall_controller_unregister()`, and `stm32_firewall_populate_bus()`. Global state is `firewall_controller_list` protected by `firewall_controller_list_lock`.

## Control Flow
Consumers parse `access-controllers` with `of_for_each_phandle()`, match each provider phandle to an already registered controller, copy firewall ID and extra args into caller storage, and optionally grant all accesses with unwind on failure. Controllers register into the global list. During `stm32_firewall_populate_bus()`, each available child must have at least one access controller; denied access causes `of_detach_node(child)` so the platform core will not probe it.

## State and Persistence
Controller registration persists in a global list until unregister. Per-device firewall data can be devm allocated by `stm32_firewall_get_grant_all_access()`, while populate-bus uses temporary allocations. Access state itself is owned by provider callbacks and may map to hardware semaphores or firmware sessions.

## Dependencies and Integration Points
The framework depends on OF phandle iteration, mutex/list infrastructure, exported STM32 firewall types, and provider callbacks. It is a central integration point between bus controllers and child drivers that need explicit access grants.

## Risks and Test Signals
Risks include probe-order dependency because providers must be registered before consumers parse phandles, possible permanent DT node detachment during denied access, mandatory `access-controllers` for firewall bus children, and no internal type filtering before calling provider grant callbacks. Test signals include successful multi-controller phandle parsing, correct unwind of granted accesses, denied children not probing, and list registration/unregistration under repeated probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/stm32_firewall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/stm32_rifsc.c -->
# sources/distributed-fs/ceph-client/drivers/bus/stm32_rifsc.c

## Purpose
This driver registers the STM32 RIFSC firewall controller, grants access to RIF-protected peripherals/memory based on security/CID/semaphore configuration, filters bus children, and optionally exposes a debugfs dump of RIFSC resource configuration.

## Important APIs, Types, and Functions
Core access functions are `stm32_rifsc_grant_access()` and `stm32_rifsc_release_access()`. Semaphore helpers `stm32_rif_acquire_semaphore()` and `stm32_rif_release_semaphore()` coordinate CID1 ownership when semaphore mode is enabled. `stm32_rifsc_probe()` maps registers, computes RISUP/RIMU/RISAL counts from `RIFSC_RISC_HWCFGR2`, registers the firewall controller, filters children, creates debugfs when enabled, and populates allowed children. Debugfs helpers read RISUP, RIMU, and RISAL register groups into printable tables.

## Control Flow
Grant access first bounds-checks the firewall ID, reads the security bit for the peripheral, denies secure-only resources, then checks CID filtering. If CID filtering is disabled, access is allowed. If semaphore mode is enabled, CID1 must be in the semaphore whitelist and the driver attempts to acquire the semaphore. Otherwise the static CID must be CID1. Release writes the semaphore register only when held.

## State and Persistence
Runtime state is the firewall controller and optional debugfs private data. Hardware state includes acquired RIF semaphores, which persist until release or reset. Debugfs reads live registers. For STM32MP21, the driver overrides an incorrect hardware RISAL count to zero.

## Dependencies and Integration Points
It depends on the STM32 firewall framework, OF matching, platform MMIO, debugfs, bitfield helpers, and SoC-specific resource-name tables. It integrates with child platform devices by detaching unauthorized nodes before population.

## Risks and Test Signals
Risks include semaphore races, failure to unregister the controller on some later probe failures, debugfs name-table bounds if hardware counts exceed compiled arrays, and CID assumptions fixed to CID1. Test signals include correct allowed/denied child probing, semaphore acquisition/release around client use, debugfs `stm32_firewall/rifsc` matching hardware, and STM32MP21 RISAL workaround behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/stm32_rifsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/sun50i-de2.c -->
# sources/distributed-fs/ceph-client/drivers/bus/sun50i-de2.c

## Purpose
This built-in Allwinner A64 Display Engine 2.0 bus driver claims the required SRAM mapping for the display engine bus and then populates child display-engine devices.

## Important APIs, Types, and Functions
`sun50i_de2_bus_probe()` calls `sunxi_sram_claim()` for the bus device and then `of_platform_populate()`. `sun50i_de2_bus_remove()` releases the SRAM claim. The driver matches `allwinner,sun50i-a64-de2` and is registered with `builtin_platform_driver()`.

## Control Flow
Probe claims SRAM before creating any children, so child display drivers only appear when the SRAM routing is available. Remove releases SRAM but does not explicitly depopulate children in this source.

## State and Persistence
The driver stores no private state. Persistent state is the SRAM ownership/routing managed by the sunxi SRAM subsystem for the lifetime of the platform device.

## Dependencies and Integration Points
It depends on OF platform population and `linux/soc/sunxi/sunxi_sram.h`. It integrates with Allwinner display-engine child nodes whose access depends on SRAM mapping.

## Risks and Test Signals
Risks are minimal but include no check of `of_platform_populate()` return value and no explicit child depopulation before SRAM release on remove. Test signals include successful SRAM claim, display-engine child probing, and failure propagation when SRAM cannot be mapped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/sun50i-de2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/sunxi-rsb.c -->
# sources/distributed-fs/ceph-client/drivers/bus/sunxi-rsb.c

## Purpose
This is the Allwinner Reduced Serial Bus controller and bus core. It registers a custom `sunxi-rsb` bus type, creates child RSB devices from DT, assigns runtime addresses to known hardware addresses, provides read/write transfers, and exposes a regmap bus for RSB client drivers.

## Important APIs, Types, and Functions
`struct sunxi_rsb` holds controller MMIO, clock, reset, completion, mutex, last IRQ status, and target clock frequency. `struct sunxi_rsb_device` and `struct sunxi_rsb_driver` are integrated through the custom bus. Exported APIs are `sunxi_rsb_driver_register()` and `__devm_regmap_init_sunxi_rsb()`. Transfer paths are `sunxi_rsb_read()`, `sunxi_rsb_write()`, and `_sunxi_rsb_run_xfer()`. Probe initializes hardware, sets device mode, registers child devices, and enables runtime PM/autosuspend.

## Control Flow
Module init registers the bus then the platform controller. Probe validates `clock-frequency`, maps registers, gets IRQ/clock/reset, initializes synchronization, requests IRQ, initializes hardware clock/reset and controller timing, sends the device-mode sequence, enables runtime PM, and calls `of_rsb_register_devices()`. Device registration first assigns runtime addresses with the `STRA` command for all known children, then creates `sunxi_rsb_device` instances so client drivers can probe. Transfers are serialized by a mutex, resume the controller via runtime PM, program address/data/command registers, and wait either by IRQ completion or atomic polling when IRQs are disabled.

## State and Persistence
The controller maintains runtime address mappings for children but uses a hardcoded map rather than dynamic allocation. `rsb->status` is set by the IRQ handler. Hardware state includes clock divider, runtime addresses in slaves, device mode, and pending transfer registers. Runtime suspend disables the clock; system suspend asserts reset and reinitializes on resume.

## Dependencies and Integration Points
It depends on CCF clocks, reset control, IRQs, OF child nodes, runtime PM, regmap, and public `linux/sunxi-rsb.h` client abstractions. Clients typically access PMICs or codecs through the exported regmap initializer.

## Risks and Test Signals
Risks include hardcoded runtime address support for only known devices, transfer timeout/abort handling, atomic-poll path differences, lost runtime addresses after full power loss unless resume reinitializes correctly, and custom bus lifetime. Test signals include PMIC regmap reads/writes of 8/16/32-bit widths, timeout/NACK error paths, suspend/resume with child devices, and clean bus unregister on module exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/sunxi-rsb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/tegra-aconnect.c -->
# sources/distributed-fs/ceph-client/drivers/bus/tegra-aconnect.c

## Purpose
This NVIDIA Tegra210 ACONNECT bus driver enables runtime PM clock control for the audio/APE connection bus and populates its child devices.

## Important APIs, Types, and Functions
`struct tegra_aconnect` stores `ape` and `apb2ape` clocks. `tegra_aconnect_probe()` validates OF, gets clocks, enables runtime PM, populates children, and logs registration. Runtime PM callbacks prepare/enable both clocks on resume and disable/unprepare them on suspend. System sleep delegates to runtime PM force suspend/resume.

## Control Flow
Probe only binds to OF-backed devices, allocates state, gets the two clocks, stores drvdata, enables PM, and immediately populates children. Child device access is expected to cause runtime PM resumes when needed.

## State and Persistence
State is limited to the two clock handles. Clock enable state persists only while runtime PM considers the bus active.

## Dependencies and Integration Points
It depends on CCF clocks, OF platform population, runtime PM, and Tegra audio bus DT nodes. It integrates with ACONNECT child devices that require `ape` and `apb2ape` clocks.

## Risks and Test Signals
Risks include ignoring `of_platform_populate()` failures, no explicit child depopulation on remove, and children depending on runtime PM links being correct. Test signals include clock toggling on runtime PM transitions, child audio device probing, and clean system suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/tegra-aconnect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/tegra-gmi.c -->
# sources/distributed-fs/ceph-client/drivers/bus/tegra-gmi.c

## Purpose
This driver configures the NVIDIA Tegra20/Tegra30 Generic Memory Interface for an external child device, usually SNOR-like parallel memory, including chip-select selection, timing registers, reset sequencing, runtime PM clock control, and child population.

## Important APIs, Types, and Functions
`struct tegra_gmi` stores MMIO base, clock, reset, and computed SNOR config/timing register values. `tegra_gmi_parse_dt()` reads one child node’s SNOR flags, chip-select from `ranges` or `reg`, and timing properties. `tegra_gmi_enable()` enables runtime PM, resets the block, writes timing/config registers, and sets `TEGRA_GMI_CONFIG_GO`. `tegra_gmi_disable()` clears GO, asserts reset, and suspends PM. Probe maps resources, gets clock/reset, initializes OPP data, parses DT, enables the controller, and populates children.

## Control Flow
Only one child is effectively supported; additional children trigger a warning. Probe computes register values before enabling hardware. If child population fails after enabling, it disables GMI. Runtime PM callbacks only gate the GMI clock; enable/disable perform the reset and programming sequence.

## State and Persistence
Computed config/timing values persist in `struct tegra_gmi` and are programmed to hardware during enable. Hardware state is lost across reset/power loss and restored only through the explicit enable path.

## Dependencies and Integration Points
It depends on OF parsing, platform MMIO, CCF clocks, reset control, runtime PM, and `devm_tegra_core_dev_init_opp_table_common()`. It integrates with the single external-memory child populated below the GMI node.

## Risks and Test Signals
Risks include limited multi-child support, chip-select decoding fallback ambiguity, no full register reprogramming in runtime resume after deep loss, and timing property truncation by bit masks without validation. Test signals include correct CS/timing register values, external memory access after probe, failure unwinding after child population errors, and runtime PM clock balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/tegra-gmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/ti-pwmss.c -->
# sources/distributed-fs/ceph-client/drivers/bus/ti-pwmss.c

## Purpose
This TI AM33xx PWM subsystem wrapper enables runtime PM for the PWMSS bus node and populates its child PWM/eCAP/eQEP-style devices.

## Important APIs, Types, and Functions
`pwmss_probe()` enables runtime PM and calls `of_platform_populate()` on the node. `pwmss_remove()` disables runtime PM. The OF match table contains `ti,am33xx-pwmss`.

## Control Flow
Probe has a simple two-step sequence: enable PM, then populate all child nodes. If child population fails it logs an error and returns the failure, but runtime PM remains enabled because there is no local unwind before returning.

## State and Persistence
There is no driver-private state and no direct MMIO access. Persistent state is runtime PM enablement for the parent bus while bound.

## Dependencies and Integration Points
It depends on OF platform population and runtime PM. It is a parent bus driver for TI PWM subsystem child devices.

## Risks and Test Signals
Risks include missing runtime PM disable on `of_platform_populate()` failure and no explicit child depopulation on remove. Test signals include child device probing, runtime PM enable/disable balance, and correct behavior when no child node is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/ti-pwmss.c -->
