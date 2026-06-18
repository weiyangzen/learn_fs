# File Research: sources/block-storage/lvm2/lib/notify/lvmnotify.h

This header declares D-Bus notification helpers:
- `lvmnotify_is_supported()`.
- `lvmnotify_send()`.
- `set_vg_notify()`, `set_lv_notify()`, `set_pv_notify()`.

Dependencies:
- Forward-declared `cmd_context`.

Role:
- Command code uses this to mark VG/LV/PV changes and send a coalesced external event.
