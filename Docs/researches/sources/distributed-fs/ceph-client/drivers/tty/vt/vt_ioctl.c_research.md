# sources/distributed-fs/ceph-client/drivers/tty/vt/vt_ioctl.c

## Purpose

`vt_ioctl.c` implements Linux virtual terminal and keyboard/display ioctl handling for console ttys. It bridges user ABI commands such as `KD*`, `VT_*`, palette/screen-map/unimap controls, font operations, process-controlled VT switching, compatibility ioctl conversion, and suspend/resume VT switching into the console, keyboard, tty, and selection subsystems.

## Important APIs, Types, and Functions

Exported or externally used functions include `vt_ioctl()`, `vt_compat_ioctl()`, `vt_waitactive()`, `vt_event_post()`, `reset_vc()`, `vc_SAK()`, `change_console()`, `vt_move_to_console()`, and exported `pm_set_vt_switch()`. `struct vt_event_wait` is the local wait-list node for `VT_WAITEVENT` and legacy active-console waits. `vt_k_ioctl()` handles keyboard/display `KD*` commands, `vt_io_ioctl()` handles palette and Unicode map operations, `vt_reldisp()` completes process-mode handshakes, and `complete_change_console()` performs the locked backend switch.

## Control Flow

`vt_ioctl()` first determines permission from controlling tty ownership or `CAP_SYS_TTY_CONFIG`, dispatches keyboard/display ioctls, then display-map ioctls, then the VT-specific switch. VT activation allocates the requested console under `console_lock` and calls `set_console()`. In `VT_PROCESS` mode, `change_console()` signals the current foreground VT owner and records `vt_newvt`; userspace later calls `VT_RELDISP` to allow or reject the switch. `complete_change_console()` switches screens, blanks/unblanks around graphics/text transitions, signals acquire events, resets dead process-controlled VTs, and posts `VT_EVENT_SWITCH`.

## State and Persistence Behavior

State is in `vc_data` fields (`vc_mode`, `vt_mode`, `vt_pid`, `vt_newvt`, geometry, font mask), global `fg_console`, `last_console`, `vt_dont_switch`, `disable_vt_switch`, `vt_events`, and keyboard state managed by helpers. No on-disk persistence exists; effects are live console mode, keymaps, fonts, palettes, Unicode maps, tty line discipline flushing, I/O permissions on x86, and process signals.

## Dependencies and Integration Points

The file depends on tty core, console locking, keyboard helpers, console font/map helpers, selection state, SAK handling, x86 `ioperm`, PM suspend helpers, pid/signal APIs, `uaccess`, and nospec array bounds hardening. It is the user ABI entry point for virtual terminal control and the kernel-internal path used by suspend code to move consoles.

## Risks and Test Signals

Risks include incorrect permission checks for mutating ioctls, process-mode switch races around `vt_newvt` and signals, missed `console_lock` protection when reading/deallocating `vc_data`, geometry resize rollback gaps, compatibility pointer conversion mistakes, event wait interruption handling, and stale graphics mode after owner death. Test signals include `KDSETMODE` blanking behavior, `VT_SETMODE` plus `VT_RELDISP` handshakes, `VT_WAITACTIVE` interruption, `VT_DISALLOCATE` busy rejection, `VT_WAITEVENT` payload conversion to 1-based VTs, compat `KDFONTOP`/unimap calls, suspend `vt_move_to_console()`, and permission denial for non-owner callers.
