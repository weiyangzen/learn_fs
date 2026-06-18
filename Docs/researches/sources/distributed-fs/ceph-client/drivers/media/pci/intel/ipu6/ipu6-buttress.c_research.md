# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-buttress.c

## Purpose
This file manages the IPU6 buttress block: subsystem power, secure-mode IPC with CSE, firmware authentication, top-level interrupt dispatch, firmware image mapping, TSC synchronization, reference-clock discovery, and restore/cleanup of buttress state.

## Important APIs, types, and functions
`ipu6_buttress_init()` initializes locks, completions, CSE IPC register offsets, interrupt enables, secure-mode state, ref-clock selection, and IPC reset. `ipu6_buttress_ipc_reset()`, `ipu6_buttress_ipc_send_bulk()`, and helpers implement the CSE doorbell/CSR protocol. `ipu6_buttress_power()` changes ISYS/PSYS power/frequency controls and polls power state. `ipu6_buttress_isr()` and `ipu6_buttress_isr_threaded()` dispatch IPU subsystem IRQs and complete IPC sends/receives. `ipu6_buttress_map_fw_image()` maps firmware into PCI DMA and IPU6 IOVA space. `ipu6_buttress_authenticate()`, `ipu6_buttress_reset_authentication()`, and `ipu6_buttress_auth_done()` drive secure firmware boot. TSC APIs are `ipu6_buttress_start_tsc_sync()`, `ipu6_buttress_tsc_read()`, and `ipu6_buttress_tsc_ticks_to_ns()`.

## Control flow and integration points
Runtime PM calls `ipu6_buttress_power()` through the bus PM domain. Secure firmware boot maps firmware/package directory, writes CSE source registers, sends BOOT_LOAD, waits for security status and bootloader magic in PSYS space, then sends AUTHENTICATE_RUN. The main IRQ reads buttress status, clears it, delegates ISYS/PSYS IRQs through `ipu6_auxdrv_data`, handles CSE IPC completions, logs fatal events, disables lines needing threaded work, and reenables them from the threaded handler.

## State, persistence, and dependencies
Persistent state is `isp->buttress`: mutexes, CSE IPC completions/register offsets, constraints list, cached watchdog value, secure mode, and ref clock. It depends on buttress register definitions, PCI DMA APIs, IPU6 DMA/MMU helpers, firmware scatterlists, completions, runtime PM, and auxiliary driver IRQ callbacks.

## Risks and test signals
High-risk areas are CSE IPC reset sequencing, timeout handling, secure/non-secure mode branching, power-state polling, IRQ storm limiting, SG firmware mapping/unmapping, and TSC rollover conversion. Test signals include successful IPC reset, firmware authentication completion, no BOOT_LOAD/AUTHENTICATE timeout, runtime PM power transitions for ISYS/PSYS, IRQ handling without stuck disabled lines, firmware unmap on errors, TSC sync success, and suspend/resume restore of IRQ/WDT state.
