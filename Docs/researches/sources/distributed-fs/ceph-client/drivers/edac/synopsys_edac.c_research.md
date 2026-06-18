# sources/distributed-fs/ceph-client/drivers/edac/synopsys_edac.c

Purpose: `synopsys_edac.c` supports Synopsys DDR controller ECC on Zynq, ZynqMP, and generic Synopsys DDRC variants. It registers a platform EDAC MC, detects ECC state and memory geometry, reports CE/UE events by polling or IRQ, and optionally supports poison injection.

Important APIs/types/functions: `struct synps_edac_priv` stores MMIO, lock, status, counters, platform data, and debug maps. `struct synps_platform_data` supplies `get_error_info`, memory type/width callbacks, quirks, and debug hooks. `zynq_get_error_info()`, `zynqmp_get_error_info()`, `handle_error()`, `get_ecc_state()`, `init_csrows()`, `mc_init()`, `setup_irq()`, `mc_probe()`, and `mc_remove()` are central.

Control flow: probe maps MMIO, reads match data, allocates chip-select/channel EDAC layers, verifies ECC, initializes MC metadata, requests IRQ if supported, registers EDAC, creates debug injection controls if enabled, and starts legacy polling counters when needed. IRQ/poll paths gather status, update totals, report EDAC events, and clear/acknowledge hardware.

State and persistence: per-device private data and hardware logs/counters persist for the device lifetime only. Status is cleared after reporting; no disk state exists.

Dependencies/integration: OF compatibles, platform MMIO/IRQ resources, EDAC core, spinlocks, `si_meminfo()`, and debug sysfs for poisoning.

Risks: total-system RAM sizing can be wrong for multi-controller layouts, quirk mistakes can lose interrupts, debug ADDRMAP decoding is complex, sysfs failure cleanup is incomplete, and error page/offset details are mostly carried in strings.

Test signals: probe each compatible, ECC-disabled rejection, polling and interrupt CE/UE paths, QoS/self-clear acknowledgement, debug poison injection, and failure cleanup.
