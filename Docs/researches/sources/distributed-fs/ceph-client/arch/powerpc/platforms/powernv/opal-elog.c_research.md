
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-elog.c

Purpose: exposes OPAL error logs as sysfs kobjects and raw binary files for userspace collection and acknowledgement.

Important APIs/types/functions: `struct elog_obj` stores log ID/type/size and buffer. `elog_event()` handles OPAL error-log event IRQs. `create_elog_obj()` creates a kobject named by log ID and a read-only `raw` bin file. `raw_attr_read()` fetches or retries the log payload using `opal_read_elog()`. `opal_elog_init()` installs the interface.

Control flow: init checks `OPAL_ELOG_READ`, creates `/sys/firmware/opal/elog`, requests `OPAL_EVENT_ERROR_LOG_AVAIL`, and asks firmware to resend pending logs if supported. On an event, it calls `opal_get_elog_size()`, clamps size to 16 KiB, deduplicates by log ID, creates an object, prefetches the payload when possible, and sends a uevent. Userspace reads `raw` and writes `acknowledge`; the store path removes the acknowledge file, calls `opal_send_ack_elog()`, and releases the kobject.

State and persistence: per-log kernel objects and buffers persist until acknowledged. Firmware persistence of logs is released only after ack.

Dependencies and integration points: OPAL elog calls, OPAL event IRQs, sysfs/kobject bin attributes, userspace log daemon behavior, and endian conversion of firmware metadata.

Risks: object lifetime races are handled similarly to dumps with extra references around bin-file creation and uevent. Oversized firmware-reported logs are clamped with a warning. Failed prefetch falls back to lazy read retry, but repeated failures expose `-EIO`.

Test signals: pending log resend at boot, event-driven log creation, duplicate event handling, raw read, ack removal and firmware ack, clamp behavior for oversized logs, and uevent race stress.
