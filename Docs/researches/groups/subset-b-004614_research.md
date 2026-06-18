# Research: subset-b-004614

Grouped research report for subset B work item `subset-b-004614`. Each section preserves the original source path and is wrapped for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-fsm9900.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-fsm9900.c

## Purpose
`emac-sgmii-fsm9900.c` contains the FSM9900-specific internal SGMII/SerDes initialization sequence for the Qualcomm EMAC driver. It programs PCS, QSERDES PLL, CDR, TX, and RX analog/digital tuning registers, starts the SerDes engine, waits for the reset state machine to report ready, and masks SGMII interrupts before the common EMAC SGMII layer enables runtime handling.

## Important APIs, Types, and Functions
- `struct emac_reg_write` is a local offset/value pair used to describe ordered hardware programming tables.
- `emac_reg_write_all()` writes one table to a supplied MMIO base with `writel()`.
- `physical_coding_sublayer_programming[]`, `sysclk_refclk_setting[]`, `pll_setting[]`, `cdr_setting[]`, and `tx_rx_setting[]` are static register programming sequences for the FSM9900 SerDes.
- `emac_sgmii_init_fsm9900()` is the exported initializer called through `struct sgmii_ops` selected by `emac_sgmii_config()`.

## Control Flow
Initialization is strictly linear: program PCS power/CDR/lane settings, set reference clock and PLL controls, program CDR and TX/RX tuning, assert `SERDES_START`, then poll `EMAC_QSERDES_COM_RESET_SM` up to `SERDES_START_WAIT_TIMES` with `usleep_range(100, 200)`. If the `READY` bit never appears, the function logs a netdev error and returns `-EIO`; otherwise it masks all SGMII interrupts and returns success.

## State and Persistence
All persistent state is in hardware registers under `adpt->phy.base`. The programming tables are immutable kernel data. No driver memory is allocated here, and no software state survives except the configured hardware state.

## Dependencies and Integration Points
The file depends on `emac.h` for shared SGMII register offsets such as wrapper CSR and lane status names, and on Linux I/O/polling helpers. It integrates with `emac-sgmii.c` via `emac_sgmii_init_fsm9900()` and with platform matching for `"qcom,fsm9900-emac-sgmii"`.

## Risks and Edge Cases
- Register constants are hardware-revision-specific; a stale table can leave the SerDes unable to lock.
- The ready poll has a fixed short retry loop, so slow hardware bring-up manifests as probe/open failure.
- The function assumes `phy->base` is valid and mapped by the common SGMII configuration path.
- Interrupts are masked at the end; later common open/link-change code must clear and enable only when ready.

## Test Signals
Useful signals are successful EMAC probe on FSM9900, no `"ser/des failed to start"` logs, stable link-up after `emac_sgmii_link_init()`, and absence of SGMII decode-error reset loops under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-fsm9900.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-qdf2400.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-qdf2400.c

## Purpose
`emac-sgmii-qdf2400.c` programs the QDF2400 SGMII v2 PHY and per-lane digital block used by the Qualcomm EMAC driver. It configures lane CDR, signal detect, TX drive, band/rate, receiver path, reset state machine bypasses, PCS power, and loopback disablement.

## Important APIs, Types, and Functions
- `struct emac_reg_write` and `emac_reg_write_all()` provide table-driven MMIO programming.
- `sgmii_laned[]` defines the QDF2400 digital lane sequence.
- `physical_coding_sublayer_programming[]` defines common PCS power/CDR/lane control values.
- `emac_sgmii_init_qdf2400()` is the hardware-specific initializer selected by ACPI `_HRV == 2`.

## Control Flow
The initializer writes PCS settings to `phy->base`, writes lane settings to `phy->digital`, clears `EMAC_SGMII_PHY_RESET_CTRL`, starts the lane reset state machine through `SGMII_LN_RSM_START`, and polls `SGMII_PHY_LN_LANE_STATUS` for bit 1. On timeout it returns `-EIO`; otherwise it disables digital and SerDes loopback registers and masks all SGMII interrupts.

## State and Persistence
State is held in hardware registers reached through `adpt->phy.base` and `adpt->phy.digital`. There is no allocation or mutable static state. The initialized state persists until reset, power loss, or reprogramming by `emac_sgmii_common_reset()`.

## Dependencies and Integration Points
The file includes `emac.h` for shared SGMII v2 offsets such as `SGMII_LN_RSM_START`, `SGMII_PHY_LN_LANE_STATUS`, and BIST/CDR registers. It is called from `emac-sgmii.c` through the ACPI-selected `qdf2400_ops`.

## Risks and Edge Cases
- `phy->digital` must be mapped; the QDF2400 path depends on resource index 1 being present.
- Several offsets differ from QDF2432 despite similar code; copying tables between revisions is risky.
- The multicast-style write loop ignores readback, so only the final ready poll catches a broad class of bad programming.
- Loopback registers are written through `phy_regs` using shared lane offsets; incorrect resource layout would silently target wrong registers.

## Test Signals
Probe/open success on QDF2400 ACPI systems, absence of `"SGMII failed to start"`, valid link negotiation through the common layer, and no decode-error-triggered SGMII resets are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-qdf2400.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-qdf2432.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-qdf2432.c

## Purpose
`emac-sgmii-qdf2432.c` provides the QDF2432-specific SGMII v2 lane and PCS programming sequence for Qualcomm EMAC. It is similar to the QDF2400 initializer but uses QDF2432 register offsets and tuned values.

## Important APIs, Types, and Functions
- Local `struct emac_reg_write` and `emac_reg_write_all()` implement table-driven register writes.
- `sgmii_laned[]` configures UCDR gains, signal detect, TX margin/pre/post, CML/mixer/VGA, band/rate, lane mode, RX path, and RSM bypasses.
- `physical_coding_sublayer_programming[]` powers the PCS and enables receive equalization.
- `emac_sgmii_init_qdf2432()` is selected for DT compatible `"qcom,qdf2432-emac-sgmii"` or ACPI `_HRV == 1`/missing `_HRV`.

## Control Flow
The function writes PCS and digital lane tables, clears PCS reset, starts the lane reset state machine, polls for `SGMII_PHY_LN_LANE_STATUS & BIT(1)`, logs and returns `-EIO` on timeout, disables loopback/BIST/CDR test registers, masks SGMII interrupts, and returns success.

## State and Persistence
State is only MMIO hardware state. The code has no locks or allocations. The configured lane state can be destroyed by hardware reset and restored by the common reset path invoking this initializer.

## Dependencies and Integration Points
It depends on the common EMAC/Sgmii headers for adapter and shared v2 offsets. It integrates with `emac-sgmii.c` through `qdf2432_ops`, ACPI matching of `QCOM8071`, and DT matching of the internal PHY node.

## Risks and Edge Cases
- Older QDF2432 ACPI tables may omit `_HRV`; the common matcher treats that as QDF2432, so this initializer must remain the conservative default.
- The code assumes both PCS and digital lane mappings are valid.
- Hardware-specific magic values need board/revision validation; failures often collapse into only the final ready timeout.

## Test Signals
The expected signs are successful initialization on QDF2432, stable SGMII lock and autonegotiation, no repeated decode-error interrupts, and working MAC reset/reinit after link faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-qdf2432.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii.c

## Purpose
`emac-sgmii.c` is the common internal SGMII PHY layer for the Qualcomm EMAC driver. It selects SoC-specific SGMII operations, maps the internal PHY resources, initializes autonegotiation, manages SGMII interrupts, and provides reset/open/close/link-change hooks to the MAC driver.

## Important APIs, Types, and Functions
- Thin exported dispatchers: `emac_sgmii_init()`, `emac_sgmii_open()`, `emac_sgmii_close()`, `emac_sgmii_link_change()`, and `emac_sgmii_reset()`.
- `emac_sgmii_link_init()` enables SGMII autonegotiation and clears forced TX/RX autoneg bits.
- `emac_sgmii_irq_clear()` implements the interrupt-clear handshake and polls status before finalizing the clear.
- `emac_sgmii_interrupt()` handles decode/disp errors, counts consecutive decode errors, and schedules MAC reinit after `DECODE_ERROR_LIMIT`.
- Common ops `emac_sgmii_common_open()`, `emac_sgmii_common_close()`, `emac_sgmii_common_link_change()`, and `emac_sgmii_common_reset()` are shared by the SoC-specific initializers.
- `emac_sgmii_config()` finds the internal PHY using ACPI child devices or DT `internal-phy`, maps resources, chooses ops, initializes SGMII, records the optional IRQ, and releases the platform-device reference.

## Control Flow
Probe-time configuration selects ops from ACPI `_HRV` or DT compatible, maps base/digital resources, calls the selected initializer, enables autonegotiation, and records an IRQ if present. Open clears and masks interrupts before registering the SGMII IRQ. Link-up clears and enables decode-error interrupts; link-down disables and synchronizes the IRQ. Interrupt handling masks to decode-related bits, increments the consecutive decode-error counter, schedules `adpt->work_thread` when the threshold is reached or when clearing fails, and acknowledges the hardware.

## State and Persistence
`struct emac_sgmii` stores MMIO mappings, optional IRQ, an atomic decode-error counter, and selected ops. Hardware state persists in the internal PHY registers. The file uses scheduled work on the parent adapter for recovery rather than resetting directly in IRQ context.

## Dependencies and Integration Points
It depends on platform resources, OF/ACPI matching, IRQ APIs, `readl_poll_timeout_atomic()`, and EMAC wrapper registers from `emac.h`. It is called by `emac_probe()`, `emac_open()`, `emac_close()`, link adjustment in the MAC/PHY path, and `emac_reinit_locked()`.

## Risks and Edge Cases
- `emac_sgmii_common_close()` unconditionally calls `free_irq(sgmii->irq, adpt)` after masking; if no IRQ was registered, callers rely on only platforms with common ops having a valid IRQ.
- ACPI child matching returns success only for known `_HRV` values; unknown hardware silently leaves no internal PHY.
- Manual `ioremap()` resources must be unmapped on remove and on all error paths.
- SGMII decode errors are treated as recoverable only after consecutive hits; intermittent errors reset the counter.
- The clear sequence uses an 8-bit status variable for a 32-bit read, matching current masks but fragile if higher interrupt bits are added.

## Test Signals
Important tests are DT and ACPI probe for each supported internal PHY, IRQ clear failure injection, link-up/down interrupt masking, repeated decode-error recovery through `work_thread`, and clean remove/unmap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii.h

## Purpose
`emac-sgmii.h` defines the interface between the EMAC core/MAC code and the internal SGMII PHY layer.

## Important APIs, Types, and Functions
- `struct sgmii_ops` contains optional `init`, `open`, `close`, `link_change`, and `reset` callbacks.
- `struct emac_sgmii` stores SGMII MMIO base, optional digital-lane MMIO base, IRQ number, atomic decode error count, and selected ops.
- Declares hardware-specific initializers for FSM9900, QDF2432, and QDF2400.
- Declares common entry points used by `emac.c` and MAC/PHY code.

## Control Flow
The header has no runtime control flow. It defines the callback contract used by `emac_sgmii_config()` to bind SoC-specific programming to the generic EMAC lifecycle.

## State and Persistence
State described here lives in `struct emac_adapter::phy`. MMIO mappings and IRQ identity are per-device resources; the decode counter is runtime recovery state.

## Dependencies and Integration Points
Forward declarations avoid direct inclusion of platform and adapter definitions. The header is included by `emac.h`, `emac.c`, and SGMII implementation files.

## Risks and Edge Cases
- Callback members are optional, so dispatchers must keep NULL guards.
- QDF2400/QDF2432 require `digital`; FSM9900 does not, but the type does not encode that distinction.
- Adding a new SoC requires both a new initializer declaration and matching ops selection.

## Test Signals
Build coverage catches declaration drift. Runtime signals are successful probe/open/close/reset through all callback combinations and no NULL dereference when an internal PHY is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac.c

## Purpose
`emac.c` is the main Qualcomm EMAC Gigabit Ethernet platform driver. It owns probe/remove/shutdown, netdev operations, IRQ/NAPI integration, clock/resource setup, PHY/SGMII setup, link recovery work, hardware statistics aggregation, and feature/MTU reconfiguration.

## Important APIs, Types, and Functions
- Public helpers: `emac_reg_update32()`, `emac_reinit_locked()`, and `emac_update_hw_stats()`.
- Netdev operations: open/stop/start_xmit/change_mtu/set_features/set_rx_mode/get_stats64/tx_timeout.
- IRQ/NAPI: `emac_isr()` masks/unmasks interrupts, handles error/TX/RX/overflow bits, and schedules NAPI; `emac_napi_rtx()` processes RX and reenables RX interrupts.
- Probe helpers: `emac_init_adapter()`, `emac_clks_get()`, `emac_clks_phase1_init()`, `emac_clks_phase2_init()`, `emac_clks_teardown()`, and `emac_probe_resources()`.
- Platform lifecycle: `emac_probe()`, `emac_remove()`, and `emac_shutdown()`.

## Control Flow
Probe sets a 46-bit DMA mask, allocates an Ethernet netdev, initializes locks/stats/IRQ masks, maps core and CSR resources, enables phase-1 clocks, configures external MDIO PHY and internal SGMII, enables phase-2 clocks, sets offload features and MTU limits, initializes rings and NAPI, registers the netdev, then logs hardware IDs. Open requests the core IRQ, allocates DMA rings, opens SGMII, and brings the MAC up. Close reverses SGMII, MAC, ring, and IRQ state under `reset_lock`. Feature/MTU changes while running call `emac_reinit_locked()`, which downs MAC, resets SGMII, and brings MAC back up. Remove unregisters netdev/NAPI, cancels work, tears down clocks and MDIO, unmaps SGMII, and frees the netdev.

## State and Persistence
`struct emac_adapter` is netdev private data and persists for the platform device lifetime. Statistics are accumulated in `adpt->stats` under a spinlock because hardware counters are read-and-accumulated. Runtime reset state is serialized by `reset_lock`; recovery is deferred to `work_thread`.

## Dependencies and Integration Points
The driver integrates with platform resources, OF/ACPI matching (`qcom,fsm9900-emac`, `QCOM8070`), clock framework, DMA API, PHY/MDIO helper in `emac-phy.c`, SGMII helper in `emac-sgmii.c`, MAC ring/data path in `emac-mac.c`, ethtool setup, NAPI, and standard Ethernet netdev APIs.

## Risks and Edge Cases
- Several error paths assume `phydev`/`mii_bus` were initialized before cleanup labels; ordering changes must preserve that.
- `emac_remove()` frees the core IRQ even though `emac_close()` also frees it for opened interfaces; unregister sequencing must prevent double-free.
- `emac_set_features()` temporarily writes `netdev->features` before reinit so MAC mode sees the new state.
- Hardware stat reads accumulate registers; concurrent readers require the documented stats lock.
- ACPI platforms skip clock management entirely, so clock bugs differ between ACPI and DT systems.
- TX timeout and SGMII decode errors converge on the same reset work path.

## Test Signals
Probe/remove under DT and ACPI, open/close cycles, MTU and VLAN feature changes while up, TX timeout recovery, interrupt-driven RX/TX under load, hardware stats monotonicity, and suspend/shutdown behavior are important regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac.h

## Purpose
`emac.h` is the central shared header for the Qualcomm EMAC driver. It defines register offsets, bit fields, clock IDs, link-speed masks, statistics layout, feature limits, IRQ and adapter state, and cross-file helper prototypes.

## Important APIs, Types, and Data
- Register offsets cover core DMA, MAC, descriptor, mailbox, interrupt, stats, timestamp, wrapper, and SGMII v2 lane/common blocks.
- Bit masks define DMA master control, interrupt status classes, mailbox indices, hardware version fields, timestamp/reset bits, and wrapper PHY controls.
- `enum emac_clk_id` indexes the driver clock array and must match `emac_clk_name[]` in `emac.c`.
- `struct emac_stats` stores accumulated RX/TX hardware counters plus a spinlock.
- `struct emac_irq` carries IRQ number and active mask.
- `struct emac_adapter` ties together netdev, MDIO PHY/bus, MMIO bases, SGMII state, stats, clocks, ring structures, DMA/ring tunables, flow control, work item, message mask, and reset lock.
- Declares `emac_reinit_locked()`, `emac_reg_update32()`, `emac_set_ethtool_ops()`, and `emac_update_hw_stats()`.

## Control Flow
The header has no executable flow. It defines the data and register contracts used by probe, MAC programming, SGMII initialization, ethtool, and PHY code.

## State and Persistence
Most persistent per-device runtime state is represented by `struct emac_adapter`. Statistics persist across hardware counter reads for the lifetime of the netdev. Ring and clock fields are initialized during probe and open.

## Dependencies and Integration Points
Includes Linux IRQ/netdev/clock/platform headers and the local MAC, PHY, and SGMII headers. Any EMAC source file that touches hardware registers or adapter state depends on these definitions.

## Risks and Edge Cases
- Register and bit definitions are hardware-specific and shared widely; mistakes have broad impact.
- `EMAC_CLK_CNT` must remain synchronized with `emac_clk_name[]`.
- Descriptor limits and MTU constants constrain ethtool, netdev, and ring allocation behavior.
- The adapter struct has no explicit ownership annotations; cleanup paths must follow probe/open ordering.

## Test Signals
Build coverage across all EMAC objects, successful hardware register programming, correct MTU/offload limit reporting, and stable ring/stat behavior after reset are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/Makefile

## Purpose
The PPE Makefile connects the Qualcomm Packet Process Engine driver to Kbuild.

## Important APIs, Types, and Data
- `obj-$(CONFIG_QCOM_PPE) += qcom-ppe.o` builds the module/object when the Kconfig symbol is enabled.
- `qcom-ppe-objs := ppe.o ppe_config.o ppe_debugfs.o` composes the driver from platform probe, hardware configuration, and debugfs counter files.

## Control Flow
Kbuild evaluates the object rules; no runtime flow exists in this file.

## State and Persistence
The file affects build graph state only. It has no runtime state.

## Dependencies and Integration Points
It depends on `CONFIG_QCOM_PPE` being defined elsewhere in the Qualcomm Ethernet Kconfig hierarchy and integrates the PPE subdirectory with the kernel build system.

## Risks and Edge Cases
Object list drift can omit required symbols or include unused objects. Renaming files or symbols requires matching Makefile updates.

## Test Signals
`CONFIG_QCOM_PPE=m` should produce a `qcom-ppe` module with all three objects linked; built-in configs should link the same objects into vmlinux.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe.c

## Purpose
`ppe.c` is the Qualcomm IPQ PPE platform driver. It maps the PPE register space through regmap, configures interconnect bandwidth and clocks, resets the hardware, applies the initial PPE hardware configuration, and sets up debugfs counters.

## Important APIs, Types, and Functions
- `ppe_icc_data[]` describes interconnect paths and default bandwidths.
- `ppe_readable_ranges[]`, `ppe_reg_table`, and `regmap_config_ipq9574` constrain readable/writable MMIO ranges and establish a 32-bit fast I/O regmap.
- `ppe_clock_init_and_reset()` fills ICC bandwidths, gets ICC paths, sets bandwidth, sets the `ppe` clock rate, enables all clocks, and asserts/deasserts reset.
- `qcom_ppe_probe()` allocates `struct ppe_device`, maps resources, initializes regmap, sets device constants, resets/configures hardware, creates debugfs, and stores drvdata.
- `qcom_ppe_remove()` tears down debugfs.

## Control Flow
Probe allocates flexible private data sized for all ICC paths, maps the first platform resource, initializes the regmap, sets IPQ9574 constants (`353 MHz`, eight ports), performs clock/ICC/reset setup, calls `ppe_hw_config()`, then exposes debugfs. Remove only removes debugfs because memory, clocks, regmap, and mappings are devm-managed.

## State and Persistence
`struct ppe_device` persists for the platform device lifetime and owns devm-managed resources plus `debugfs_root`. Hardware register state persists after `ppe_hw_config()` until reset or driver removal.

## Dependencies and Integration Points
The file depends on platform device resources, regmap MMIO, reset controller, clock bulk APIs, and interconnect APIs. It integrates with `ppe_config.c` for hardware init and `ppe_debugfs.c` for observability. DT matching uses `"qcom,ipq9574-ppe"`.

## Risks and Edge Cases
- Regmap access ranges must include every register touched by config and debugfs; missing ranges cause regmap failures.
- `devm_clk_bulk_get_all_enabled()` enables all clocks after setting only the common `ppe` rate.
- ICC defaults use `Bps_to_icc(ppe_rate)` for zero entries, so clock-rate changes alter bandwidth requests.
- Debugfs creation failure is non-fatal; hardware can run without observability.

## Test Signals
Probe success, correct reset timing, no regmap access errors during `ppe_hw_config()`, debugfs directory creation, and successful remove without dangling debugfs entries are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe.h

## Purpose
`ppe.h` defines the core private device structure shared by the PPE platform, configuration, and debugfs files.

## Important APIs, Types, and Data
- Forward declares `struct device`, `struct regmap`, and `struct dentry`.
- `struct ppe_device` stores the kernel device, regmap, PPE clock rate, number of ports, debugfs root, ICC path count, and a flexible counted `icc_paths[]` array.

## Control Flow
No runtime flow exists. The header defines shared state layout.

## State and Persistence
`struct ppe_device` is allocated at probe and persists until device removal. The flexible ICC path array is allocated with `struct_size()` according to the platform driver's path count.

## Dependencies and Integration Points
The header includes interconnect definitions and is consumed by `ppe.c`, `ppe_config.c`, `ppe_debugfs.c`, and their companion headers.

## Risks and Edge Cases
The flexible array depends on correct allocation sizing and `num_icc_paths`. Any future per-SoC port/count differences need fields initialized before configuration helpers consume them.

## Test Signals
Build checks for `__counted_by()` support and runtime probe with the expected number of ICC paths validate the structure contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_config.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_config.c

## Purpose
`ppe_config.c` applies the IPQ9574 PPE hardware initialization policy. It configures buffer management, queue management, scheduler arbitration, per-port scheduler resources, queue destinations, service codes, counters, RSS hash generation, queue-to-ring maps, and initial bridge/VSI behavior.

## Important APIs, Types, and Functions
- Local config types describe BM port thresholds, QM queue thresholds, scheduler directions, BM/QM scheduler entries, port scheduler loops, and per-port resource ranges.
- Static tables define IPQ9574 buffer group limits, BM port configs, QM queue configs, BM/QM scheduler order, port scheduler nodes, and scheduler resources.
- Exported APIs: `ppe_queue_scheduler_set()`, `ppe_queue_ucast_base_set()`, `ppe_queue_ucast_offset_pri_set()`, `ppe_queue_ucast_offset_hash_set()`, `ppe_port_resource_get()`, `ppe_sc_config_set()`, `ppe_counter_enable_set()`, `ppe_rss_hash_config_set()`, `ppe_ring_queue_map_set()`, and `ppe_hw_config()`.
- Internal stages: `ppe_config_bm()`, `ppe_config_qm()`, `ppe_config_scheduler()`, `ppe_queue_dest_init()`, `ppe_servcode_init()`, `ppe_port_config_init()`, `ppe_rss_hash_init()`, `ppe_queues_to_ring_init()`, and `ppe_bridge_init()`.

## Control Flow
`ppe_hw_config()` runs a fixed sequence and stops on first regmap error. BM config sets shared buffer group 0 and per-port flow-control thresholds. QM config sets queue group buffer limits, initializes unicast/multicast queues, enables enqueue/dequeue, and enables queue counters. Scheduler config programs BM and QM arbitration tables, then loops per-port scheduler node templates through L0/L1 mapping helpers. Queue destination init assigns per-port unicast bases, priority offsets, and zeroed hash offsets. Service code init configures EDMA bypass service code 1. Port config enables counters and MTU/MRU actions. RSS init seeds IPv4/IPv6 hash registers using `get_random_u32()`. Ring init maps CPU-port queues to EDMA ring 0. Bridge init constrains initial forwarding to CPU port 0 until higher-level switch/VSI support attaches ports.

## State and Persistence
All durable state is written into PPE hardware tables through regmap. The only randomized state is the RSS hash seed generated during initialization. No software state is retained beyond the `ppe_device` reference and static configuration tables.

## Dependencies and Integration Points
The file depends heavily on `ppe_regs.h` field definitions and regmap bulk/update APIs. It is invoked by `qcom_ppe_probe()` and provides exported configuration helpers likely intended for later Ethernet/switchdev/EDMA integration.

## Risks and Edge Cases
- Static resource tables assume `ppe_dev->num_ports == 8` plus one reserved resource entry; incorrect port count can index unexpected resource rows.
- `ppe_port_resource_get()` allows `port == num_ports` for the reserved row but rejects only greater values.
- Queue/multicast table addressing for multicast queues uses queue IDs directly against multicast table base, so hardware table numbering assumptions are critical.
- RSS seed is intentionally random, making exact register state nondeterministic across boots.
- Many helpers trust caller-provided IDs and bitmaps; invalid queue/profile/service values can program outside intended hardware ranges if not validated by callers.
- Regmap errors abort config, but partial hardware programming is not rolled back.

## Test Signals
Regression tests should validate probe-time `ppe_hw_config()` on IPQ9574, regmap write ranges, per-port resource outputs, RSS register programming for IPv4/IPv6, service-code bitmap encoding, queue-to-ring bitmaps, and debugfs counters increasing after traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_config.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_config.h

## Purpose
`ppe_config.h` publishes PPE configuration constants, enums, data structures, and helper prototypes used to configure scheduler, queue, service-code, counter, RSS, and ring-mapping behavior.

## Important APIs, Types, and Data
- Queue base constants define destination-port, CPU-code, and service-code mapping regions.
- RSS constants define IPv4/IPv6 modes, tuple counts, IP mix length, and ring-to-queue bitmap size.
- `enum ppe_scheduler_frame_mode`, `struct ppe_scheduler_cfg`, and `enum ppe_resource_type` describe scheduler inputs and resources.
- `struct ppe_queue_ucast_dest` describes the selector used for unicast queue base lookup.
- Service-code bypass enums split ingress, egress, counter, and tunnel bypass bitmaps; `struct ppe_sc_bypass` stores them with `DECLARE_BITMAP()`.
- `struct ppe_sc_cfg` describes service-code destination, bypass, next-code, and EIP action fields.
- `enum ppe_action_type` defines forward/drop/copy/redirect action values.
- `struct ppe_rss_hash_cfg` describes RSS mask, fragment behavior, seed, mix fields, and final mix selectors.
- Function prototypes expose the configuration entry points implemented in `ppe_config.c`.

## Control Flow
No executable flow exists. The header establishes the contract for caller-supplied values that are later encoded into hardware registers.

## State and Persistence
Structures are caller-owned until encoded into hardware. Bitmaps are embedded in `struct ppe_sc_cfg`; RSS and scheduler configs are passed by value.

## Dependencies and Integration Points
Includes Linux types and `ppe.h`. It is consumed by PPE hardware config and debugfs, and it is the public internal API for future PPE users in the Qualcomm Ethernet stack.

## Risks and Edge Cases
- Enum values are hardware bit positions; reordering would change register encodings.
- Bitmap sizes deliberately exclude unspecified hardware gaps but preserve numeric holes, so callers must use the named enums.
- Several prototypes accept raw integer IDs without type-safe range encoding.
- `PPE_RING_TO_QUEUE_BITMAP_WORD_CNT` assumes 300 queues represented by ten 32-bit words.

## Test Signals
Build coverage catches struct/prototype drift. Unit or hardware tests should verify service-code bitmaps, resource IDs, RSS tuple arrays, and queue bitmap width.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_debugfs.c

## Purpose
`ppe_debugfs.c` exposes PPE hardware counters through debugfs. It reads, formats, and clears counters for buffer manager, parser, RX/TX ports, VLAN, L2 forwarding, CPU codes, and queue manager activity.

## Important APIs, Types, and Functions
- `enum ppe_cnt_size_type` describes one-word, three-word, and five-word counter table layouts.
- `enum ppe_cnt_type` selects counter families.
- `struct ppe_debugfs_entry` is per-file debugfs private data containing file name/type and PPE device pointer.
- `debugfs_files[]` creates files: `bm`, `parse`, `port_rx`, `vlan_rx`, `l2_forward`, `cpu_code`, `vlan_tx`, `port_tx`, and `qm`.
- `ppe_pkt_cnt_get()` reads counters and reconstructs 32-bit drop counts for five-word tables.
- `ppe_tbl_pkt_cnt_clear()` clears counter locations.
- Family readers print only nonzero counters through `seq_file`.
- `ppe_packet_counter_show()` dispatches reads; `ppe_packet_counter_write()` clears the selected family.
- `ppe_debugfs_setup()` and `ppe_debugfs_teardown()` create/remove `/sys/kernel/debug/ppe`.

## Control Flow
Setup creates a root directory and allocates a private entry for each counter file. Reading a file dispatches by `counter_type` and scans the relevant hardware tables, printing grouped nonzero counters. Writing any data to a file clears that file's associated counters. Teardown recursively removes the root.

## State and Persistence
Debugfs entry memory is devm-allocated. Counter state lives in PPE hardware registers and is mutable through the write handler. The root dentry is stored in `ppe_device`.

## Dependencies and Integration Points
Depends on debugfs, seq_file, regmap, PPE register definitions, and `ppe_device`. It is optional observability for the PPE platform driver and is set up after hardware configuration.

## Risks and Edge Cases
- Files are created with mode `0444` but use `DEFINE_SHOW_STORE_ATTRIBUTE`; if write access is desired, mode and fops expectations should be checked.
- Counter clearing ignores individual regmap write failures.
- Long scans, especially CPU-code and queue tables, can be expensive on slow regmap backends.
- Five-word drop count reconstruction assumes the documented split across words 2 and 3.
- If devm allocation fails mid-loop, setup returns with a partially populated debugfs directory.

## Test Signals
Mount debugfs and read each PPE file after probe, generate traffic to observe nonzero counters, write to clear families where mode permits, and check remove cleans `/sys/kernel/debug/ppe`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_debugfs.h

## Purpose
`ppe_debugfs.h` declares the PPE debugfs setup and teardown hooks.

## Important APIs, Types, and Functions
- Includes `ppe.h` for `struct ppe_device`.
- Declares `ppe_debugfs_setup(struct ppe_device *ppe_dev)`.
- Declares `ppe_debugfs_teardown(struct ppe_device *ppe_dev)`.

## Control Flow
No control flow exists in the header. The platform driver calls setup after hardware config and teardown during remove.

## State and Persistence
No state is owned here; the functions mutate `ppe_device::debugfs_root` and debugfs entries in the implementation.

## Dependencies and Integration Points
Integrates `ppe.c` with `ppe_debugfs.c` while keeping debugfs details out of the platform driver.

## Risks and Edge Cases
The header assumes `ppe.h` is sufficient for the device type. Any future debugfs build option split would need stubs or conditional declarations.

## Test Signals
Successful PPE build/link and visible debugfs files after probe validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_regs.h

## Purpose
`ppe_regs.h` is the hardware register and table definition header for the Qualcomm IPQ PPE driver. It names register/table bases, entry counts, increments, bit fields, and helper macros for BM, QM, scheduler, service-code, RSS, VLAN, bridge, port, L2, counter, and drop-count blocks.

## Important APIs, Types, and Data
- Register/table groups cover BM scheduler/drop/flow control, RSS hash, service-code tables, egress VLAN/bridge, VSI, MRU/MTU, L2 virtual ports, RX/TX/drop counters, tunnel/parser counters, scheduler L0/L1 tables, ring queue maps, enqueue/dequeue controls, admission-control queues/groups, and multicast/unicast drop counters.
- Uses `GENMASK()`, `BIT()`, and `FIELD_MODIFY()` helper macros to encode multiword tables.
- Address helper macros such as `PPE_CPU_PORT_MULTICAST_FORCE_DROP_CNT_TBL_ADDR()` encode table layout for debugfs.

## Control Flow
The header has no runtime flow. It provides compile-time constants consumed by `ppe_config.c` and `ppe_debugfs.c`.

## State and Persistence
No software state is owned here. The definitions describe persistent hardware state in the PPE MMIO region.

## Dependencies and Integration Points
Includes `linux/bitfield.h`. It must remain consistent with `ppe.c` regmap access ranges, `ppe_config.c` programming logic, and `ppe_debugfs.c` counter scanning.

## Risks and Edge Cases
- Incorrect address, increment, or entry-count definitions can make regmap access fail or corrupt unrelated hardware tables.
- Multiword `FIELD_MODIFY()` macros depend on callers passing sufficiently large arrays.
- Counter table sizes differ by subsystem; using the wrong size type misreads or clears counters.
- Some hardware comments describe reserved or unspecified values; enum/table users must preserve numeric positions.

## Test Signals
Compile-time use by all PPE objects, successful regmap writes during `ppe_hw_config()`, valid debugfs counter reads, and hardware traffic counters matching expected table indices are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k.c

## Purpose
`qca_7k.c` implements low-level QCA7000/QCA7K SPI register access helpers and SPI error handling shared by the SPI netdev driver.

## Important APIs, Types, and Functions
- `qcaspi_spi_error()` marks the device out of sync and increments `spi_err` when an SPI transaction fails while ready.
- `qcaspi_read_register()` builds a two-transfer internal-register read command and returns a host-endian 16-bit value.
- `__qcaspi_write_register()` performs the raw internal-register write.
- `qcaspi_write_register()` optionally verifies writes by reading back and retrying up to the caller-supplied count.

## Control Flow
Read/write helpers assemble big-endian SPI command words using `QCA7K_SPI_READ/WRITE | QCA7K_SPI_INTERNAL | reg`, handle legacy mode by splitting command and data into separate `spi_sync()` calls, then return SPI/message status. Verified writes loop until readback matches or retries are exhausted.

## State and Persistence
The functions mutate `qca->sync` and statistics on errors. Successful calls persist values in QCA7K internal registers.

## Dependencies and Integration Points
Depends on Linux SPI and netdev APIs plus `qca_7k.h`/`qca_spi.h`. Higher-level SPI driver code uses these helpers for signature checks, interrupt masking/ack, buffer sizing, reset control, and watermarks.

## Risks and Edge Cases
- `qcaspi_spi_error()` ignores errors before ready, so early sync failures rely on caller logic.
- Verified writes return a boolean mismatch value after retry exhaustion rather than a conventional negative errno.
- Legacy mode doubles transaction boundaries and is timing-sensitive.
- Callers must serialize access through the SPI thread/driver path where appropriate.

## Test Signals
Good signature reads, successful interrupt enable/cause writes, write-verify stats staying at zero, and recovery from induced SPI failures validate the helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k.h

## Purpose
`qca_7k.h` defines QCA7000/QCA7K SPI command bits, register addresses, interrupt bits, buffer sizes, and low-level helper prototypes.

## Important APIs, Types, and Data
- Command flags distinguish read/write and internal/external address spaces.
- Defines command length, hardware packet-length overhead, and hardware buffer length.
- Register addresses cover buffer size, write-buffer space, read-buffer bytes, SPI config/status, interrupt cause/enable, watermarks, signature, and action control.
- Interrupt bits cover write-buffer watermark, CPU-on, address/write/read buffer errors, and packet availability.
- Declares `qcaspi_spi_error()`, `qcaspi_read_register()`, and `qcaspi_write_register()`.

## Control Flow
No runtime flow exists. The constants are used to build SPI transactions and interpret interrupts.

## State and Persistence
The header describes on-chip register state and interrupt bits. It owns no software state.

## Dependencies and Integration Points
Includes `qca_spi.h`, which creates a circular include relationship resolved by include guards. It is used by SPI register helpers, the SPI netdev driver, and debug/ethtool register dumping.

## Risks and Edge Cases
Register address and bit definitions are protocol contracts; mistakes break synchronization, reset, or data movement. The hardware buffer length constrains TX ring sizing and RX validation.

## Test Signals
Successful signature reads (`0xAA55`), interrupt handling, and TX/RX buffer-space accounting are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k_common.c

## Purpose
`qca_7k_common.c` implements the QCA7K serial Ethernet framing format used by both SPI and UART transports. It creates frame headers/footers and decodes byte streams into Ethernet frames with a state machine.

## Important APIs, Types, and Functions
- `qcafrm_create_header()` writes four `0xAA` bytes, little-endian payload length, and two reserved bytes.
- `qcafrm_create_footer()` writes two `0x55` footer bytes.
- `qcafrm_fsm_decode()` consumes one byte at a time and returns gather/error/completed-frame status.
- All three functions are exported with `EXPORT_SYMBOL_GPL`.

## Control Flow
The decoder starts either at SPI hardware-length states or UART header states, validates the four-byte header, reads two length bytes and two reserved bytes, rejects lengths larger than the supplied buffer or smaller than minimum Ethernet frame length, copies payload bytes while using the state value as remaining length, then validates both footer bytes and returns the completed frame length.

## State and Persistence
Decoder state lives in caller-owned `struct qcafrm_handle` and receive buffer. The file has no static mutable state. Frame decode progress persists across calls until a complete frame or error resets the state.

## Dependencies and Integration Points
Used by `qca_spi.c` and `qca_uart.c` for RX decode and by both TX paths for header/footer creation. It depends on Ethernet/VLAN length constants from the header.

## Risks and Edge Cases
- On `QCAFRM_NOHEAD`, callers generally ignore the error and keep scanning, which is expected for stream resynchronization.
- `QCAFRM_INVFRAME` is defined but not emitted by the current decoder.
- The function writes payload bytes directly to `buf[handle->offset]`; callers must pass a buffer with adequate tailroom.
- SPI mode consumes four hardware-length bytes before the Atheros frame header, while UART mode does not.

## Test Signals
Decoder unit tests should cover valid SPI/UART frames, split frames across calls, missing header/footer, invalid lengths, minimum Ethernet padding, VLAN-sized maximum frames, and resynchronization after noise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k_common.h

## Purpose
`qca_7k_common.h` defines the shared QCA7K Ethernet-over-serial framing protocol contract for SPI and UART drivers.

## Important APIs, Types, and Data
- Error/status constants include `QCAFRM_GATHER`, `QCAFRM_NOHEAD`, `QCAFRM_NOTAIL`, `QCAFRM_INVLEN`, and `QCAFRM_INVFRAME`.
- MTU/frame constants define Ethernet min/max MTU, min/max frame lengths, header length, and footer length.
- `enum qcafrm_state` encodes SPI hardware-length states, header-byte states, length/reserved states, payload countdown, and footer states.
- `struct qcafrm_handle` stores current state, initial state, and an offset/temporary length.
- Inline initializers choose SPI or UART initial states.
- Declares header/footer creation and FSM decode functions.

## Control Flow
The header has inline initialization flow only: SPI starts at `QCAFRM_HW_LEN0`; UART starts at `QCAFRM_WAIT_AA1`.

## State and Persistence
`struct qcafrm_handle` is per receiver and persists across serial callbacks or SPI burst reads. Its `offset` field doubles as temporary length storage during header parsing.

## Dependencies and Integration Points
Includes Ethernet/VLAN headers and is consumed by QCA SPI and UART netdev drivers plus the common implementation.

## Risks and Edge Cases
State enum values intentionally count downward through negative values and then positive payload lengths; changing them can break decode logic. Buffer-size and MTU constants must remain consistent with both transports' skb allocation.

## Test Signals
Build and transport tests should verify both `qcafrm_fsm_init_spi()` and `qcafrm_fsm_init_uart()` produce decodable streams for their respective hardware framing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_debug.c

## Purpose
`qca_debug.c` provides QCA7000 SPI driver debugfs and ethtool support. It exposes runtime SPI/netdev state, driver information, fixed link settings, statistics strings/data, selected SPI registers, and ring-parameter configuration.

## Important APIs, Types, and Functions
- `qcaspi_gstrings_stats[]` must match `struct qcaspi_stats` field order.
- Debugfs, when enabled, provides an `info` file under a directory named after the netdev device.
- Ettool callbacks include driver info, link ksettings, stats, strings, set count, register dump, and ringparam get/set.
- `qcaspi_set_ethtool_ops()` installs the ethtool ops on the netdev.

## Control Flow
Debugfs setup creates a directory and readonly info file; removal recursively deletes it. Ettool register dump reads selected SPI registers with `qcaspi_read_register()`. Ringparam update validates RX settings, parks the SPI thread if running, clamps TX pending between min and max, updates `txr.count`, and unparks the thread.

## State and Persistence
Debugfs state is `qca->device_root`. Ettool stats read `qca->stats` directly. Ring count changes persist in `qca->txr.count` until netdev teardown or another update.

## Dependencies and Integration Points
Depends on debugfs, ethtool, seq_file, `qca_7k.h`, and `qca_spi.h`. It is called from `qcaspi_netdev_setup()`, `qca_spi_probe()`, and `qca_spi_remove()`.

## Risks and Edge Cases
- Stats export relies on exact layout/order matching between strings and `struct qcaspi_stats`.
- Register dumping performs live SPI reads and can disturb error counters if SPI is failing.
- Ringparam update does not reallocate the fixed skb pointer array; it only changes active ring depth.
- Debugfs creation failures are ignored.

## Test Signals
`ethtool -i`, stats, register dump, ringparam get/set, debugfs `info`, and stable operation while changing TX ring size validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_debug.h

## Purpose
`qca_debug.h` declares the debugfs and ethtool setup hooks for the QCA7000 SPI driver.

## Important APIs, Types, and Functions
- Includes `qca_spi.h` for `struct qcaspi`.
- Declares `qcaspi_init_device_debugfs()`, `qcaspi_remove_device_debugfs()`, and `qcaspi_set_ethtool_ops()`.

## Control Flow
No runtime flow exists in the header.

## State and Persistence
No state is owned here. The implementation uses `struct qcaspi` fields for debugfs and statistics.

## Dependencies and Integration Points
Used by `qca_spi.c` to install observability during netdev setup/probe and remove it during device removal.

## Risks and Edge Cases
The header includes the full SPI private header, tying debug declarations to SPI implementation details. Any future non-SPI QCA debug reuse would need a narrower interface.

## Test Signals
Successful QCA SPI build/link and installed ethtool ops on the netdev validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_spi.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_spi.c

## Purpose
`qca_spi.c` implements a QCA7000 Ethernet-over-SPI netdev driver. It manages SPI synchronization/reset, interrupt-driven RX, queued TX through a kernel thread, serial frame encoding/decoding, module parameters, netdev lifecycle, DT probing, and debug/ethtool integration.

## Important APIs, Types, and Functions
- Module parameters configure SPI clock, burst length, pluggable signature policy, and write verification retries.
- SPI transfer helpers move external FIFO data in burst or legacy mode.
- TX path: `qcaspi_netdev_xmit()` frames/pads/skb-queues packets; `qcaspi_transmit()` drains queued frames when device write-buffer space is available.
- RX path: `qcaspi_receive()` reads available bytes, runs `qcafrm_fsm_decode()`, and submits completed skbs through `netif_rx()`.
- Sync path: `qcaspi_qca7k_sync()` handles unknown/reset/ready states, signature checks, slave reset bit, CPU-on events, and reset timeouts.
- Thread/IRQ: `qcaspi_spi_thread()` is the serialized worker for sync, interrupt handling, RX, and TX; `qcaspi_intr_handler()` sets a flag and wakes it.
- Netdev/probe: open starts the thread and enables IRQ, close disables interrupts and stops the thread, probe validates DT/module params, configures SPI mode, allocates/registers netdev, requests IRQ, sets MAC address, optionally checks signature, and creates debugfs.

## Control Flow
Interrupts set `SPI_INTR` and wake the SPI thread. The thread synchronizes the device, disables carrier and flushes TX while not ready, handles interrupt causes by acknowledging CPU-on/read/write-buffer events, receives packets when ready, and transmits queued packets when write-buffer space allows. TX from the network stack only frames and enqueues skbs under netdev TX locking; actual SPI I/O is centralized in the thread.

## State and Persistence
`struct qcaspi` holds netdev/SPI pointers, thread, TX ring, stats, RX buffer/SKB, sync state, framing FSM, flags, reset counter, debugfs root, and user options. Hardware state includes QCA7K registers and FIFOs. Statistics persist until netdev teardown.

## Dependencies and Integration Points
Depends on Linux SPI, kthread, IRQ, netdev, OF MAC-address helpers, and the common QCA7K framing and register helpers. DT compatible is `"qca,qca7000"`. It integrates with `qca_debug.c` for ethtool/debugfs.

## Risks and Edge Cases
- Ring state uses fixed array storage but configurable active depth; invalid updates must remain clamped.
- `qcaspi_netdev_xmit()` updates `txr.size` before the thread drains; TX lock coverage is important for consistency.
- Sync recovery flushes queued TX and drops in-progress RX frames on CPU-on.
- Buffer-availability values larger than hardware max are treated as line interference and trigger retries/resets.
- Return paths sometimes use `NETDEV_TX_BUSY` after allocation failure, which can cause retry semantics rather than an immediate drop.
- Legacy mode changes transaction structure and has a TODO for GPIO reset.

## Test Signals
Probe with valid/invalid module params, signature failure for non-pluggable devices, open/close thread and IRQ lifecycle, RX frame decode under burst reads, TX ring full/wake behavior, SPI error reset recovery, ethtool stats/registers, and ringparam changes are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_spi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_spi.h

## Purpose
`qca_spi.h` defines private constants, TX ring layout, statistics, and per-device state for the QCA7000 SPI Ethernet driver.

## Important APIs, Types, and Data
- Driver identity/version constants and protocol limits such as good signature, TX ring min/max, RX frame batch max, sync states, reset timeout, and sync event IDs.
- `struct tx_ring` stores a fixed skb pointer array plus head/tail/size/count.
- `struct qcaspi_stats` stores reset, error, memory, ring, SPI, verify, buffer, and signature counters.
- `struct qcaspi` is netdev private state for the SPI device, thread, ring, stats, RX buffers, sync state, framing handle, flags, reset count, optional debugfs root, legacy mode, and burst length.

## Control Flow
The header has no executable flow. Its constants drive sync state machines, ring management, and runtime validation in `qca_spi.c`.

## State and Persistence
All fields in `struct qcaspi` persist for the netdev lifetime. TX ring entries own queued skbs until transmitted or flushed. Stats persist until the netdev is freed.

## Dependencies and Integration Points
Includes netdev, scheduler, skb, SPI, and common framing headers. It is included by low-level register helpers, SPI driver code, and QCA debug/ethtool code.

## Risks and Edge Cases
- `tx_ring::size` tracks bytes including hardware packet overhead, not just skb payload.
- `sync` is a small integer state shared by thread and error helpers.
- The fixed `QCASPI_TX_RING_MAX_LEN` array constrains ethtool ringparam changes.
- Debugfs field is conditional on `CONFIG_DEBUG_FS`, while helper declarations remain unconditional through stubs.

## Test Signals
TX ring enqueue/drain/flush, stats string count matching struct field count, reset state transitions, and burst/legacy mode operation validate the structure contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_uart.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_uart.c

## Purpose
`qca_uart.c` implements a QCA7000 Ethernet-over-UART netdev using the serdev framework and the shared QCA7K framing protocol.

## Important APIs, Types, and Functions
- `struct qcauart` stores netdev, spinlock, TX work, serdev, framing handle, RX skb, and TX buffer pointers/counts.
- `qca_tty_receive()` decodes received serial bytes through `qcafrm_fsm_decode()` and submits completed Ethernet frames.
- `qcauart_netdev_xmit()` builds a framed/padded packet in a preallocated TX buffer, writes as much as serdev accepts, stops the netdev queue, and records remaining bytes.
- `qcauart_transmit()` continues writing pending TX bytes from workqueue context and wakes the queue when complete.
- `qca_uart_probe()` allocates/registers the netdev, configures serdev callbacks, baud rate, flow control, MAC address, carrier state, and framing FSM.

## Control Flow
Probe opens the serdev, sets baud and flow control, then registers the netdev. Netdev open starts the queue. TX stops the queue until the work item, triggered by serdev write wakeups, drains the pending buffer. RX callback processes incoming bytes immediately and may allocate a new skb after each completed frame. Remove unregisters netdev, closes serdev, cancels TX work, and frees the netdev.

## State and Persistence
Per-device state is netdev private data. TX state persists in `tx_buffer`, `tx_head`, and `tx_left` across partial serdev writes. RX framing state persists across receive callbacks. Carrier is set on at probe because UART has no SPI-style sync.

## Dependencies and Integration Points
Depends on serdev, OF MAC/current-speed properties, netdev APIs, and `qca_7k_common`. DT compatible is `"qca,qca7000"`, shared with the SPI binding but used on a serdev bus.

## Risks and Edge Cases
- TX uses one buffer and stops the queue, so only one packet can be in flight.
- `tx_packets` increments when TX buffer drains, while `tx_bytes` increments only by the first write amount, not necessarily the full framed or payload length.
- RX path must set `rx_skb->dev`; the initial skb relies on allocation helper context and subsequent protocol assignment.
- No explicit carrier/sync validation exists for UART beyond serial open.
- Spinlock usage mixes `spin_lock()` in xmit and `spin_lock_bh()` in work/close.

## Test Signals
Serdev probe with `current-speed`, open/close queue state, TX partial-write wakeups, RX frame decode, timeout accounting, random/static MAC assignment, and remove cleanup are the primary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/Kconfig

## Purpose
`rmnet/Kconfig` defines the RMNET MAP driver configuration option.

## Important APIs, Types, and Data
- `menuconfig RMNET` is a tristate labeled "RmNet MAP driver".
- Defaults to disabled.
- Selects `GRO_CELLS`.
- Help text describes MAP multiplexing and aggregation over IP-mode physical devices.

## Control Flow
Kconfig controls whether the rmnet module is built. No runtime flow exists in this file.

## State and Persistence
The selected value persists in kernel `.config` and determines build output.

## Dependencies and Integration Points
The option feeds `rmnet/Makefile` through `CONFIG_RMNET` and ensures GRO cell support required by the virtual netdev data path.

## Risks and Edge Cases
Selecting `GRO_CELLS` pulls in additional networking support. With the option disabled, rtnetlink kind `"rmnet"` is unavailable even if userspace expects it.

## Test Signals
`CONFIG_RMNET=m` should build `rmnet.ko`; disabled configs should omit the module and rtnl link kind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/Makefile

## Purpose
The rmnet Makefile defines the object composition of the RMNET MAP module.

## Important APIs, Types, and Data
- `rmnet-y` includes `rmnet_config.o`, `rmnet_vnd.o`, `rmnet_handlers.o`, `rmnet_map_data.o`, and `rmnet_map_command.o`.
- `obj-$(CONFIG_RMNET) += rmnet.o` builds the aggregate module when enabled.

## Control Flow
Kbuild combines the listed objects into `rmnet.o` according to `CONFIG_RMNET`. There is no runtime control flow here.

## State and Persistence
The file controls build graph state only.

## Dependencies and Integration Points
Consumes the Kconfig symbol and includes config, virtual device, handler, data MAP, and command MAP implementation files.

## Risks and Edge Cases
Adding a new rmnet source file requires this list to be updated. Removing an object that owns exported internal symbols will cause link failures or missing functionality.

## Test Signals
Building RMNET as a module and built-in should link all listed objects and expose the `"rmnet"` rtnl link kind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_config.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_config.c

## Purpose
`rmnet_config.c` implements RMNET's rtnetlink configuration engine. It registers the `"rmnet"` link kind, associates real devices with RMNET ports, creates/deletes muxed virtual devices, changes mux IDs and data-format flags, handles bridge mode, and cleans up when underlying devices unregister.

## Important APIs, Types, and Functions
- `rmnet_policy[]` validates `IFLA_RMNET_MUX_ID` and `IFLA_RMNET_FLAGS`.
- Real-device helpers register/unregister `rmnet_rx_handler` and allocate/free `struct rmnet_port`.
- `rmnet_newlink()` creates a mux endpoint and virtual rmnet netdev on a real device.
- `rmnet_dellink()` removes a virtual endpoint, bridge state, upper links, and real-device registration when no endpoints remain.
- `rmnet_changelink()` changes mux ID and data-format flags with MTU validation/rollback.
- `rmnet_fill_info()` reports mux ID and flags to rtnetlink.
- Exported helpers: `rmnet_get_port_rcu()`, `rmnet_get_endpoint()`, `rmnet_add_bridge()`, `rmnet_del_bridge()`, and `rmnet_get_port_rtnl()`.
- Module init/exit register the netdevice notifier and rtnl link ops.

## Control Flow
Creating a link requires `IFLA_LINK` and a valid mux ID, finds the real device, allocates an endpoint, registers the real device rx handler if needed, creates the virtual rmnet device through `rmnet_vnd_newlink()`, links it as an upper device, inserts the endpoint into the mux hash bucket, and applies flags. Deletion removes bridge state first, deletes the endpoint from RCU hlist, unlinks uppers, unregisters the real device if empty, and queues virtual netdev unregister. Netdevice notifier force-cleans RMNET state on real device unregister and rejects MTU changes that invalidate attached rmnet devices.

## State and Persistence
Per-real-device `struct rmnet_port` is stored as `rx_handler_data`. Per-mux `struct rmnet_endpoint` objects live in RCU hlist buckets. Data-format flags, bridge endpoints, aggregation state, and rmnet device counts persist until link deletion or forced cleanup.

## Dependencies and Integration Points
Depends on rtnetlink, netdevice rx handlers, upper/lower device links, RCU hlist traversal, rmnet MAP handlers, virtual netdev helpers, and aggregation helpers. Userspace integrates through `ip link add/change ... type rmnet`.

## Risks and Edge Cases
- Mux ID range is 0-254 because `RMNET_MAX_LOGICAL_EP` is 255.
- Bridge mode is mutually constrained with multiplexed rmnet devices; more than one rmnet dev prevents bridging.
- Error paths must free endpoints, unregister real devices, and undo virtual device creation in the right order.
- Data-format changes roll back if resulting MTU is invalid.
- Forced unassociation must handle both real-device and bridge-device roles.
- RCU endpoint lookup requires callers to hold appropriate RCU or rtnl protection.

## Test Signals
Rtnetlink tests should cover newlink without link/mux, duplicate mux IDs, changelink mux moves, flag changes with MTU rollback, deleting endpoints, real-device unregister cleanup, bridge add/delete, and module init/exit registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_config.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_config.h

## Purpose
`rmnet_config.h` defines the shared RMNET configuration data structures for real-device ports, mux endpoints, aggregation state, virtual device stats, private netdev state, and configuration helper prototypes.

## Important APIs, Types, and Data
- `RMNET_MAX_LOGICAL_EP` limits mux endpoint buckets to 255.
- `struct rmnet_endpoint` maps a mux ID to an egress virtual netdev and hlist node.
- `struct rmnet_egress_agg_params` and aggregation fields in `struct rmnet_port` track MAP egress aggregation.
- `struct rmnet_port` represents one real device registered with rmnet, including data format, mode, mux endpoint buckets, bridge links, rmnet device pointer, aggregation locks/timers/work, and counts.
- `struct rmnet_vnd_stats`, `struct rmnet_pcpu_stats`, and `struct rmnet_priv_stats` hold virtual-device and checksum statistics.
- `struct rmnet_priv` is per-rmnet-netdev private state with mux ID, real device, percpu stats, GRO cells, and checksum stats.
- Declares rtnl ops and configuration helpers.

## Control Flow
The header contains no executable flow. It defines state that data-path handlers, virtual-device code, MAP aggregation, and rtnetlink configuration code share.

## State and Persistence
`struct rmnet_port` persists while a real device is associated with rmnet. `struct rmnet_priv` persists for each virtual rmnet netdev. Aggregation timers/work and skb aggregation pointers persist across packets until flushed.

## Dependencies and Integration Points
Includes skb/time and GRO cells support. It is included by config, handlers, virtual-device, MAP data, and MAP command files.

## Risks and Edge Cases
- Aggregation state has its own spinlock and timer/work items; cleanup ordering must cancel or flush them before freeing the port.
- `muxed_ep` uses 255 hlist heads, so mux ID validation must reject 255 and higher.
- Statistics mix u64 sync-protected per-CPU counters and plain private counters; readers must use matching synchronization.
- Bridge and virtual-device modes share fields in `struct rmnet_port`, so mode transitions must be explicit.

## Test Signals
Creating/deleting rmnet links, data-path demux by mux ID, aggregation flush/cleanup, GRO cell behavior, and per-CPU stats reads validate this header's contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_config.h -->
