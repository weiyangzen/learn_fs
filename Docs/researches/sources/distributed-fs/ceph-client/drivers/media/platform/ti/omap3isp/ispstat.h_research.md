# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispstat.h

## Purpose
Defines the generic OMAP3 ISP statistics ABI between common `ispstat.c` and concrete AF/AEWB/histogram engines.

## Important APIs, Types, and Functions
Defines buffer states (`STAT_BUF_DONE`, `STAT_NO_BUF`, `STAT_BUF_WAITING_DMA`), pool/event sizes, `struct ispstat_buffer`, `struct ispstat_ops`, `enum ispstat_state_t`, `struct ispstat`, and `struct ispstat_generic_config`. The ops table requires validate, set, register setup, enable, busy, and optional buffer-processing callbacks.

## Control Flow
Concrete engines embed or own a `struct ispstat`, fill `priv`, `recover_priv`, `event_type`, and `ops`, then call the public helpers for config, enable, stream, ISR, and statistics requests. The common layer drives the engine through the callback table and uses the state enum to sequence disabled, enabling, enabled, disabling, and suspended transitions.

## State and Persistence
The header specifies long-lived per-engine state: coherent buffer pool pointers, DMA channel, active/locked buffers, counters, wait accumulation, update flags, and ioctl mutex. It is kernel-memory state only and is reset by cleanup or driver removal.

## Dependencies and Integration Points
Includes Linux OMAP3 ISP UAPI definitions for userspace statistic data, V4L2 event support, ISP core headers, and generic `ispvideo` pipeline structures. Module-specific files must keep their config structures compatible with `ispstat_generic_config` field ordering.

## Risks and Edge Cases
The comment on `ispstat_generic_config` is a structural contract: `buf_size` and `config_counter` must match the beginning of multiple UAPI config structs. Misordered fields would corrupt validation/config-counter behavior. Callback implementations must be callable under the locking/IRQ expectations imposed by `ispstat.c`.

## Test Signals
Compile concrete stats engines, verify each initializes with correct ops/event type, check UAPI config structures still match generic layout, and exercise suspend/resume plus stream enable/disable transitions.
