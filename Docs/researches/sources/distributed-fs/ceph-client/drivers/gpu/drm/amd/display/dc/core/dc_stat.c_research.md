# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_stat.c

## Purpose

`dc_stat.c` provides lockless Display Core status accessors for DMUB notifications and GPINT dataout. The file-level documentation states these interfaces are called without DAL and DC locks, so they must avoid modifying shared DC state except variables exclusively owned by these interfaces.

## Important APIs, types, and functions

- `dc_stat_get_dmub_notification` obtains `dc->ctx->dmub_srv->dmub`, calls `dmub_srv_stat_get_notification`, asserts success, and normalizes certain notification instances from DPIA port index to DC link index with `get_link_index_from_dpia_port_index`.
- `dc_stat_get_dmub_dataout` calls `dmub_srv_get_gpint_dataout` and asserts success.
- Key types are `struct dc`, `struct dmub_notification`, `struct dmub_srv`, and `enum dmub_status`.

## Control flow

Both functions are thin pass-throughs to DMUB service routines. Notification retrieval has one post-processing branch: for HPD, HPD IRQ, AUX reply, DPIA notification, and SET_CONFIG_REPLY notification types, `notify->link_index` is overwritten with the DC link index derived from `notify->instance`.

## State and persistence behavior

The functions do not allocate memory or persist state. They read DC context pointers and write only caller-provided output buffers (`notify` or `dataout`). The notification helper mutates the returned notification structure after DMUB fills it.

## Dependencies and integration points

Includes are `dc/dc_stat.h`, `dmub/dmub_srv_stat.h`, and `dc_dmub_srv.h`. The code integrates DC with DMUB firmware status queues and the DPIA/link-index mapping helper used by USB4/DPIA display paths. It is likely consumed by higher-level interrupt, HPD, AUX, or DM status polling code that cannot take the normal DC locks.

## Risks and edge cases

- The code assumes `dc`, `dc->ctx`, `dc->ctx->dmub_srv`, and `dmub` are valid. There is no defensive NULL check.
- Because the functions are explicitly lockless, adding access to mutable DC fields would be risky.
- `ASSERT(status == DMUB_STATUS_OK)` may catch firmware/service failures in debug builds, but non-debug behavior depends on ASSERT semantics; callers still receive whatever data the DMUB layer produced.
- Notification instance remapping is type-gated. New DMUB notification types that carry DPIA port indexes must be added here or consumers may see the wrong index namespace.

## Test signals

Exercise DMUB notification retrieval for HPD, HPD IRQ, AUX reply, DPIA notification, SET_CONFIG_REPLY, and unrelated notification types. Check that DPIA instances map to expected `link_index` values and that non-remapped types preserve DMUB-provided fields. Also cover GPINT dataout reads and DMUB failure injection where ASSERT diagnostics are expected.
