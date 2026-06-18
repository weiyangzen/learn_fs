# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_resource.h

## Purpose

`link_resource.h` declares link resource accessor helpers for current resources and HPO resource-map preservation.

## Important APIs, Types, And Functions

It declares `link_get_cur_res_map()`, `link_restore_res_map()`, and `link_get_cur_link_res()`.

## Control Flow

No runtime flow exists in the header. The declarations are assigned into `link_service` by `link_factory.c`.

## State And Persistence Behavior

No state is stored. The implementation reads current pipe contexts and mutates caller outputs plus verified link capabilities during resource-map restore.

## Dependencies And Integration Points

It includes `link_service.h` for `struct dc`, `struct dc_link`, and `struct link_resource`.

## Risks And Edge Cases

Callers must provide valid output pointers. The restore API mutates link verified caps, so it is not a pure restore of an external map and should be called only in the intended resource reconciliation phase.

## Test Signals

Build coverage catches signature drift. Runtime validation comes from HPO DP resource allocation and mode validation around multiple DP2-capable links.
