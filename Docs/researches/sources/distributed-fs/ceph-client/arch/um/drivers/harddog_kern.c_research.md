<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/harddog_kern.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/harddog_kern.c

Purpose: implements the UML `/dev/watchdog` misc driver. It presents the Linux watchdog character-device ABI and delegates actual timeout enforcement to the host `uml_watchdog` helper.

Important APIs/types/functions: file operations are `harddog_open()`, `harddog_release()`, `harddog_write()`, `harddog_ioctl_unlocked()`, and mutex-wrapped `harddog_ioctl()`. Global state includes `timer_alive`, `harddog_in_fd`, `harddog_out_fd`, `harddog_mutex`, and `lock`. `harddog_miscdev` registers minor `WATCHDOG_MINOR`.

Control flow: open enforces single-open, optionally obtains the mconsole notify socket, starts the watchdog helper, and records FDs. Writes and `WDIOC_KEEPALIVE` call `ping_watchdog()`. Release closes both helper pipes through `stop_watchdog()` and marks the timer inactive. Ioctl supports `WDIOC_GETSUPPORT`, status/bootstatus zero, and keepalive.

State and persistence: runtime state is global watchdog open state and host pipe FDs. No persistent watchdog settings are stored; timeout is handled externally by the helper.

Dependencies and integration points: depends on miscdevice/watchdog ABI, mconsole notification when available, module nowayout behavior, and host functions from `harddog_user.c`.

Risks: locking combines a mutex and spinlock around single-open and FD state. `CONFIG_WATCHDOG_NOWAYOUT` takes a module reference but release still calls stop, so behavior should be checked against expected nowayout semantics. Helper startup failure must leave state clean.

Test signals: open exclusivity, keepalive writes, ioctl support/status, helper missing/failing cases, close behavior, mconsole notify socket mode, and modular unload with active watchdog.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/harddog_kern.c -->
