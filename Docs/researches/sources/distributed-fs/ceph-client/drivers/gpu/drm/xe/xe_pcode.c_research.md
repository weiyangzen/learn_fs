<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode.c

## Purpose

`xe_pcode.c` centralizes communication with PCODE firmware through MMIO mailbox registers. It provides serialized read/write/request helpers, PCODE readiness polling for dGFX, and initialization of the minimum GT frequency QOS table.

## Important APIs and Functions

The public API includes `xe_pcode_init()`, `xe_pcode_probe_early()`, `xe_pcode_ready()`, `xe_pcode_read()`, `xe_pcode_write_timeout()`, `xe_pcode_write64_timeout()`, `xe_pcode_write()`, `xe_pcode_request()`, and `xe_pcode_init_min_freq_table()`. `pcode_mailbox_status()` translates PCODE error codes into Linux errno values. `__pcode_mailbox_rw()` performs the raw mailbox transaction, while `pcode_mailbox_rw()` asserts `tile->pcode.lock`. `pcode_try_request()` repeatedly sends a request and checks masked replies.

## Control Flow and State

Each mailbox transaction checks `skip_pcode`, verifies the mailbox is not already ready/busy, writes DATA0/DATA1, writes `PCODE_READY | mbox`, waits for the ready bit to clear, optionally reads reply data, then decodes status. Public read/write APIs take `tile->pcode.lock`. `xe_pcode_request()` starts with sleepable retry, then logs and retries for 50 ms with preemption disabled if the short timeout path did not acknowledge. `xe_pcode_ready()` polls root tile PCODE init status for up to three minutes on dGFX. Persistent state is the per-tile mutex and PCODE firmware/hardware state behind the mailbox.

## Dependencies and Integration Points

It depends on `xe_mmio_wait32()`, PCODE register definitions, device/platform flags, DRM managed mutex init, delay primitives, and error injection. PCI early probe and PM resume call readiness checks; GT frequency management and power/thermal features consume mailbox helpers and constants.

## Risks and Test Signals

Timeouts and firmware status mapping are failure-critical. `xe_pcode_request()` returns `status ? status : ret`, where `status` is an errno-like value filled by mailbox attempts, so callers must handle PCODE-specific negative errors. Atomic retry disables preemption and must remain bounded. Tests should cover busy mailbox `-EAGAIN`, skip-pcode no-op behavior, all decoded PCODE error codes, read/write64 data ordering, request timeout fallback, max/min frequency table bounds, three-minute readiness timeout, and error injection during PCI probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode.c -->
