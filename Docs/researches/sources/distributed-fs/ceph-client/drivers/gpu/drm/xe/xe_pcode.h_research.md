<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode.h

## Purpose

`xe_pcode.h` is the public PCODE firmware mailbox interface for Xe components.

## Important APIs

The header declares initialization and readiness functions, synchronous mailbox read/write helpers, 64-bit write support, a retrying request helper, and `xe_pcode_init_min_freq_table()`. The `xe_pcode_write()` macro is a one millisecond timeout wrapper. `PCODE_MBOX(mbcmd, param1, param2)` builds mailbox command words using `PCODE_MB_COMMAND`, `PCODE_MB_PARAM1`, and `PCODE_MB_PARAM2` fields from `xe_pcode_api.h`.

## Control Flow and State

Callers initialize the per-tile PCODE mutex with `xe_pcode_init()`, wait for firmware readiness during early probe or resume, then issue serialized mailbox commands through the helpers. State resides in hardware PCODE registers and the per-tile lock.

## Dependencies and Integration Points

It relies on PCODE bit definitions from `xe_pcode_api.h` being visible to macro users and is consumed by PM, GT frequency/power, thermal, fan, and late-binding firmware code.

## Risks and Test Signals

Mailbox helper timeouts are caller-selected, so users must choose realistic values. Compile tests should verify macro field definitions are available. Integration tests should verify callers hold no conflicting locks that can deadlock while waiting for PCODE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode.h -->
