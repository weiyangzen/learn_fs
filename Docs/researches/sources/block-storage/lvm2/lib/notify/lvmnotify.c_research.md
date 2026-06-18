# File Research: sources/block-storage/lvm2/lib/notify/lvmnotify.c

This file implements optional D-Bus notifications to `lvmdbusd`.

Build modes:
- With `NOTIFYDBUS_SUPPORT`, uses systemd `sd-bus`.
- Without it, notification APIs are stubs and `lvmnotify_is_supported()` returns 0.

Main APIs:
- `lvmnotify_is_supported()`.
- `lvmnotify_send(struct cmd_context *cmd)`.
- `set_vg_notify()`, `set_lv_notify()`, `set_pv_notify()`.

Behavior:
- Notification flags on `cmd` are coalesced; if none are set, no action is taken.
- Before sending, flags are cleared.
- `lvmdbusd_running()` checks the daemon lock file, using `LVM_DBUSD_LOCKFILE` env override or `/var/lock/lvm/lvmdbusd`, and determines running state by lock availability.
- `lvmnotify_send()` avoids starting the daemon implicitly, opens system bus, calls `ExternalEvent` with the command name, parses integer result, and logs warnings only for unexpected failures.

Dependencies:
- `cmd_context`, `get_cmd_name()`, sd-bus, lock file protocol used by lvmdbusd.

Correctness notes:
- Unexpected lock-file errors are treated as “daemon running” to avoid missing notifications.
- Known service-not-present errors are debug-level only.

Risks:
- Notifications are best-effort; failures do not fail the LVM command path.
