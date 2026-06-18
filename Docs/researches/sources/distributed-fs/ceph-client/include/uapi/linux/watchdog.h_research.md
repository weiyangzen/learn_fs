<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/watchdog.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/watchdog.h

Purpose: defines generic watchdog character-device ioctls, capability/status structures, and option/status flags.

Important APIs and types: `struct watchdog_info` reports supported options, firmware version, and identity. `WDIOC_*` ioctls get support/status/bootstatus/temp/timeouts/timeleft, set options, keepalive, and set pretimeout. `WDIOF_*` option flags report reset causes and capabilities; `WDIOS_*` status flags enable/disable card and temperature panic.

Control flow, state, and persistence: userspace opens a watchdog, queries capabilities, sets timeout/pretimeout, periodically sends keepalive, and may enable/disable or magic-close depending on driver support. Hardware timer state persists until disabled, reset, or device close semantics.

Dependencies and integration points: integrates watchdog core, platform watchdog drivers, systemd/watchdog daemons, and reboot/panic handling.

Risks and test signals: risks include ioctl direction quirks, timeout unit mismatch, magic close behavior, and pretimeout support drift. Test keepalive, timeout set/get, bootstatus, magic close, pretimeout interrupt, and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/watchdog.h -->
