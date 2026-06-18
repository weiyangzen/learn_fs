# sources/distributed-fs/ceph-client/drivers/usb/host/uhci-debug.c

## Purpose
`uhci-debug.c` supplies UHCI schedule introspection. It is included directly by `uhci-hcd.c`, giving it access to static UHCI helpers and private types. With dynamic debug and debugfs enabled, it formats TDs, QHs, root-hub registers, periodic load tables, frame-list contents, and skeleton queues for debug logs or `/sys/kernel/debug/uhci/<bus>`.

## Important APIs, Types, And Functions
`uhci_show_td()` prints hardware TD link/status/token/buffer fields and decodes status flags, PID, endpoint, device address, toggle, and expected length. `uhci_show_urbp()` summarizes per-URB private state and TD lists. `uhci_show_qh()` prints QH hardware pointers, queue type, periodic parameters, URB chains, and dummy TD. `uhci_show_status()` dumps controller registers and first two port status registers. `uhci_sprint_schedule()` is the central formatter for root-hub state, HC status, load table, frame list consistency, and skeleton QH lists. Debugfs file operations allocate a snapshot buffer in open, allow read/lseek, and free it on release.

## Control Flow
When `CONFIG_DYNAMIC_DEBUG` is active, debug helpers emit detailed schedule snapshots. `uhci_irq()` uses `uhci_sprint_schedule()` to log a schedule after fatal halt conditions when debug level is high. `uhci_start()` creates a debugfs file per bus when `UHCI_DEBUG_OPS` is available. Opening that file grabs `uhci->lock`, snapshots the schedule into a 64 KiB buffer, then releases the lock so user reads do not hold controller state. When dynamic debug is disabled, stub versions compile away formatting.

## State And Persistence Behavior
The file owns `uhci_debugfs_root` and temporary debug buffers only. It does not alter controller state except by reading registers and private structures under lock. Debug output is a point-in-time snapshot; no persistent state is stored.

## Dependencies And Integration Points
The code relies on UHCI private types and macros from `uhci-hcd.h`, controller register access helpers, Linux debugfs, dynamic debug, and user-copy helpers. Since it is included into `uhci-hcd.c`, its static symbols are local to the UHCI translation unit. `uhci_hcd_init()` creates the root debugfs directory, and `release_uhci()` removes per-controller files.

## Risks And Edge Cases
Formatting uses `sprintf()` into fixed buffers while checking after writes, so the code reserves `EXTRA_SPACE` and truncates with ellipses. Debug output walks hardware/software schedules that may be inconsistent during failures; it must tolerate mismatched frame-list links and empty queues. Because it reads hardware registers, callers must ensure the controller is accessible before invoking detailed status dumps. Pointer output is intentionally diagnostic and not an ABI.

## Test Signals
Build combinations with and without `CONFIG_DYNAMIC_DEBUG` and `CONFIG_DEBUG_FS` should compile. Runtime signals include a debugfs `uhci/<bus>` file, readable schedule output, no lockdep complaints while opening under traffic, and useful fatal-halt log output when debug level is elevated.
