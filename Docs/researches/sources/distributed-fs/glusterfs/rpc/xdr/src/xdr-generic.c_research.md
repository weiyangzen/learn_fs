# sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-generic.c

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-generic.c` implements generic iovec-to-XDR helpers used by the RPC/NFS wrapper layer. It serializes typed structures into caller-provided buffers, decodes buffers into typed structures, exposes remaining payload bytes for nocopy paths, and rounds payload lengths to XDR alignment when GNFS is enabled. The source was read as a complete 127-line file for this report.

## Important APIs, Types, and Functions

Exports are `xdr_serialize_generic`, `xdr_to_generic`, `xdr_to_generic_payload`, `xdr_length_round_up`, `xdr_bytes_round_up`, and `xdr_vector_round_up`. They depend on the `PROC` macro from the header to call `xdrproc_t` portably across Linux/BSD/macOS signature differences.

## Control Flow

Serialize and decode helpers validate buffer/data/procedure pointers, create an `XDR` memory stream with `xdrmem_create`, call the supplied XDR procedure, and return the encoded/decoded length or `-1`. The payload variant additionally returns the unconsumed portion of the XDR stream through `pendingpayload` under `BUILD_GNFS`. Round-up helpers compute 4-byte XDR padding and adjust a single iovec or the last vector in a vector list.

## State and Persistence Behavior

The file owns no persistent state. It only mutates caller-provided output buffers, decoded argument structures, and optional iovec lengths. `xdr_to_generic_payload` exposes pointers into the input buffer, so the input buffer must remain valid while the pending payload is used.

## Dependencies and Integration Points

It depends on SunRPC XDR APIs, `struct iovec`, and compatibility macros from `glusterfs/compat.h`. It is used by `msg-nfs3.c` and other RPC message wrappers that want uniform iovec handling.

## Risks and Edge Cases

Without `BUILD_GNFS`, payload and round-up helpers mostly return defaults/no-ops, so callers must be compiled consistently with GNFS expectations. Length macros depend on XDR internals (`x_private`, `x_base`, `x_handy`), which can be portability-sensitive. Nocopy payload pointers are only valid as long as the source iovec storage is valid. The hardcoded `1048576` buffer-size argument in `xdr_vector_round_up` is a policy assumption for padding safety.

## Test Signals

Round-trip tests using representative XDR procedures, null pointer failure tests, short output buffer tests, nocopy payload extraction tests, and XDR padding tests with lengths 0 through several modulo-4 cases are useful. Cross-platform compile tests validate `PROC`.
