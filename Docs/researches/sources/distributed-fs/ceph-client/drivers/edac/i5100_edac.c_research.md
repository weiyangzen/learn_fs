# sources/distributed-fs/ceph-client/drivers/edac/i5100_edac.c

## Purpose
This PCI EDAC driver supports Intel 5100 memory controllers. It models two independent channels as EDAC channel/slot layers, decodes memory technology and interleave registers, reports nonfatal memory errors, maintains periodic hardware scrubbing, and provides debugfs error injection.

## Important APIs and Functions
Many inline accessors decode MC/SPD/MIR/DMIR/MTR/VALIDLOG/REC/NREC fields. `struct i5100_priv` stores DIMM rank maps, interleave maps, MTR data, PCI devices, scrubbing work, injection settings, and debugfs directory. Error flow is handled by `i5100_check_error()`, `i5100_read_log()`, `i5100_handle_ce()`, and `i5100_handle_ue()`. Scrubbing is managed by `i5100_refresh_scrubbing()`, `i5100_set_scrub_rate()`, and `i5100_get_scrub_rate()`. Injection uses `i5100_do_inject()` and debugfs file operations.

## Control Flow
Probe binds device 16 function 1, enables ECC error detection, unmasks nonfatal memory errors, obtains channel memory-map devices and the injection device, allocates EDAC layers, starts scrub maintenance if BIOS already enabled it, reads SPD-derived DIMM rank layout, reads interleave/MTR state, initializes DIMMs, normalizes op state, registers EDAC, and sets up debugfs. Polling reads first/next nonfatal memory registers, selects the channel, reads valid logs from the channel device, reports CE/UE records, then clears logs and status.

## State and Persistence
Per-controller state includes PCI references, scrubbing delayed work, DIMM/interleave topology, injection masks, and debugfs dentries. Scrubbing state is maintained periodically while enabled. Hardware error masks and injection registers are modified at runtime.

## Dependencies and Integration
The driver uses PCI config access, EDAC memory-controller APIs, EDAC core work/debugfs helpers, delayed work, SPD-over-chipset commands, and Intel 5100 PCI IDs.

## Risks
The file explicitly notes that EDAC cannot fully represent the two independent channels, so csrows are laid out channel-by-channel. SPD access is polling-based and waits until not busy without a bounded loop after command issue. Debug injection directly writes hardware injection control. Scrubbing cancellation must use sync cancellation on removal/failure.

## Test Signals
Signals include ECC-disabled probe rejection, DIMM labels and sizes from SPD/MTR data, CE/UE reports from channel valid logs, scrub rate get/set behavior and delayed work requeueing, debugfs injection files, and balanced PCI disable/put paths on all failures.
