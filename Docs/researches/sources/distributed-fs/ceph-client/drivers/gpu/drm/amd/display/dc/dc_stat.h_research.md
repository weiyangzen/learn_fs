# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_stat.h

## Purpose
`dc_stat.h` declares lock-light status accessors for DMUB notifications and dataout. The file explicitly documents that these interfaces are called without DAL/DC locks and therefore may only access variables exclusively defined for this use.

## Important APIs
`dc_stat_get_dmub_notification` retrieves a `struct dmub_notification` from a `dc`. `dc_stat_get_dmub_dataout` retrieves a `uint32_t` dataout value.

## Control Flow And State
There is no implementation in this header. The state contract is important: implementation must avoid general DC state mutation or lock-dependent reads because callers use it outside the normal locking regime.

## Dependencies And Integration Points
It includes `dc.h` and `dmub/dmub_srv.h`, integrating with DMUB status reporting, interrupt paths, diagnostics, and display manager polling.

## Risks
Lockless access risks stale or torn reads unless the implementation uses dedicated atomic or otherwise safe storage. Expanding these APIs to touch broader DC state would violate the documented constraint.

## Test Signals
Concurrency tests, lockdep/static review, DMUB notification delivery tests, and interrupt/polling stress are relevant.
