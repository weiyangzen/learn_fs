
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/guest-state-buffer.c

## Purpose
Implements guest state buffer construction, parsing, bitmap iteration, and message send/receive helpers for PowerPC nested/pseries guest state exchange. It serializes typed guest-state elements into hypervisor buffers and wraps `H_GUEST_SET_STATE` / `H_GUEST_GET_STATE` hcalls.

## Important APIs, Types, And Functions
Exports allocation and buffer helpers `kvmppc_gsb_new()`, `kvmppc_gsb_free()`, `kvmppc_gsb_put()`, element helpers `__kvmppc_gse_put()`, `kvmppc_gse_parse()`, ID metadata helpers `kvmppc_gsid_flags()`, `kvmppc_gsid_size()`, `kvmppc_gsid_mask()`, parser helpers `kvmppc_gsp_insert()`, `kvmppc_gsp_lookup()`, bitmap helpers `kvmppc_gsbm_set()`, `kvmppc_gsbm_clear()`, `kvmppc_gsbm_test()`, `kvmppc_gsbm_next()`, message helpers `kvmppc_gsm_init()`, `kvmppc_gsm_new()`, `kvmppc_gsm_size()`, `kvmppc_gsm_free()`, `kvmppc_gsm_fill_info()`, `kvmppc_gsm_refresh_info()`, and hcall wrappers `kvmppc_gsb_send()`/`kvmppc_gsb_recv()`.

## Control Flow
Buffers are allocated with power-of-two capacity and start with a big-endian header element count. Adding an element validates the ID's expected size, appends a `struct kvmppc_gs_elem`, copies data, and increments the header count. Parsing iterates serialized elements, validates lengths against ID metadata, and builds a flattened-ID lookup table plus iterator bitmap. Message helpers delegate sizing/fill/refresh to caller-provided `struct kvmppc_gs_msg_ops`. Send/receive translate internal flags to hcall flags and pass the physical buffer address to firmware.

## State And Persistence
State is heap-allocated per `struct kvmppc_gs_buff` and `struct kvmppc_gs_msg`. Parser state stores pointers into an existing buffer, so it is valid only while that buffer remains alive and unchanged. The file encodes class/type/mask knowledge in static switch logic and a size table.

## Dependencies And Integration Points
Depends on `asm/guest-state-buffer.h`, hcall definitions/wrappers, Linux allocation helpers, endian helpers, bit operations, and exported symbols for nested/pseries KVM code. It is directly tested by `test-guest-state-buffer.c`.

## Risks
`kvmppc_gsb_put()` intentionally does not check capacity; callers should use higher-level put functions that validate size first. Parser lookup aliases duplicate IDs to the last parsed element. `kvmppc_gsm_refresh_info()` checks `fill_info` instead of `refresh_info` before calling refresh, which looks suspicious and should be reviewed. Buffers passed to hcalls must be physically addressable and sized for firmware expectations.

## Test Signals
KUnit tests cover buffer allocation, element insertion, parser lookup, bitmap iteration, message fill/refresh, and host-wide counter retrieval. Additional tests should cover invalid IDs, invalid lengths, duplicate elements, near-capacity insertion, missing `refresh_info`, and hcall error propagation.
