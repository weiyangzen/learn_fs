# sources/distributed-fs/ceph-client/drivers/pps/kc.c

Purpose: optional kernel consumer bridge from PPS events to the kernel NTP `hardpps()` discipline.

Important APIs/functions: `pps_kc_bind()`, `pps_kc_remove()`, and `pps_kc_event()`.

Control flow: `PPS_KC_BIND` ioctl reaches `pps_kc_bind()`, which under a spinlock either unbinds the current device when edge is zero, binds the source if no other source is active or the same source is rebinding, or rejects competing consumers. `pps_kc_remove()` clears the binding if a source is being removed. `pps_kc_event()` checks whether the event came from the bound source and matches the selected edge mask, then calls `hardpps()` with realtime and raw timestamps.

State/dependencies: global `pps_kc_hardpps_dev` and `pps_kc_hardpps_mode` protected by `pps_kc_hardpps_lock`. Depends on `CONFIG_NTP_PPS`, timex/hardpps, and PPS core.

Risks: only one kernel consumer source can be bound system-wide; bind/unbind must not be called from interrupt context; source removal must reliably clear binding; edge validation is split between ioctl and bind function.

Test signals: bind assert and clear modes, reject second source, unbind wrong source, remove bound source, and verify `hardpps()` invocation under PPS events when `CONFIG_NTP_PPS=y`.
