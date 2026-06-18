<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/console.c -->
# sources/distributed-fs/ceph-client/kernel/power/console.c

Purpose: Saves/restores virtual console state around suspend/resume and lets drivers declare whether a VT switch is required.

Important APIs/types/functions: `pm_vt_switch_required()`, `pm_vt_switch_unregister()`, `pm_prepare_console()`, and `pm_restore_console()`. Key state includes `orig_fgconsole`, `orig_kmsg`, `vt_switch_done`, `vt_switch_mutex`, `pm_vt_switch_list`, and `struct pm_vt_switch`.

Control flow: Drivers register/update their switch requirement in a mutex-protected list. `pm_vt_switch()` returns true if no driver has registered, console suspend is disabled, or any registered driver requires switching; otherwise it skips switching. `pm_prepare_console()` moves to the reserved suspend console and redirects kmsg. `pm_restore_console()` moves back and restores kmsg redirection if a switch was done or current requirements indicate switching.

State and persistence: Runtime state tracks registered devices and original console/kmsg destinations. Entries are allocated per registering device and removed on unregister. No persistent storage is used.

Dependencies/integration: Integrates with VT console helpers, keyboard/VT state, `console_suspend_enabled`, PM suspend/resume sequencing, device drivers, and module exports.

Risks: Device unregister must remove list entries to avoid stale pointers. The switch decision can change between prepare and restore, so `vt_switch_done` protects restore behavior. Allocation failure in `pm_vt_switch_required()` leaves the previous behavior unchanged. The reserved console is `MAX_NR_CONSOLES-1`, so assumptions must match VT limits.

Test signals: no registered drivers, all drivers switchless, one driver requiring switch, no-console-suspend command-line behavior, registration update for an existing device, unregister cleanup, failed console move, and suspend/resume cycles with kmsg redirection restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/console.c -->
