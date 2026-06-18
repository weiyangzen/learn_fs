# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth_ptp.h

## Purpose
This header defines ICSSM shared-RAM offsets and helper calculations for PTP/time-sync data exchanged with firmware. It covers RX/TX timestamp slots, notification bytes, domain and correction fields, time-sync compare/period control, single-step metadata, and small mode-control flags.

## Important APIs, types, and functions
- Offset macros define firmware locations for RX Sync/Pdelay timestamps, TX timestamp notifications, TX timestamps, correction fields, compare/period settings, link-local and E2E/UDP controls, previous timestamps, clock identity, and scratch memory.
- The anonymous enum defines PTP event indices: Sync, Delay Request, Delay Response, and count.
- `PRUETH_PTP_TS_SIZE`, notify size, and mask define record widths.
- `TIMESYNC_CTRL_BG_ENABLE` and `TIMESYNC_CTRL_FORCED_2STEP` describe control bits.
- `icssm_prueth_tx_ts_offs_get(port, event)` computes a TX timestamp offset for a port/event pair.
- `icssm_prueth_tx_ts_notify_offs_get(port, event)` computes the matching notification byte offset.

## Control flow
The header has only inline offset math. `icssm_prueth.c` uses the offsets in `icssm_ptp_dram_init()` to initialize correction, RCF, compare period, domain list, relay behavior, HSR tag mode, and E2E/UDP timestamping before starting firmware and IEP support.

## State and persistence behavior
PTP state is volatile firmware shared memory. The host writes initial values at interface open; firmware updates timestamp and notification fields at runtime. No persistent storage is involved.

## Dependencies and integration points
The macros rely on Linux `BIT()` being available through includers. The runtime integration point is the ICSS IEP driver used by `icssm_prueth.c`; firmware must interpret these offsets exactly.

## Risks and edge cases
- Offset overlap is high risk because fields are tightly packed and comments indicate byte sizes rather than C structures.
- The helper functions assume linear per-port/per-event layout starting at port 0.
- A firmware layout change without synchronized driver updates would break timestamp delivery or time-sync control.

## Test signals
Test interface open initializes expected shared-RAM values; PTP event timestamp offsets produce the expected P1/P2 slots; hardware timestamp traffic should produce notification byte changes and valid timestamp reads in firmware/driver integration tests.
