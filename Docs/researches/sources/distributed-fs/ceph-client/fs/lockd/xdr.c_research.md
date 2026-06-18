# sources/distributed-fs/ceph-client/fs/lockd/xdr.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/xdr.c` provides hand-written server XDR support for legacy NLM v1/v3 procedures. It decodes request arguments into `struct nlm_args`, encodes `struct nlm_res` replies, and translates legacy 32-bit offset/length lock ranges to VFS `file_lock` ranges. The source was read as a complete 354-line file for this report.

## Important APIs, Types, and Functions

Local helpers include `s32_to_loff_t`, `loff_t_to_s32`, `svcxdr_decode_fhandle`, `svcxdr_decode_lock`, `svcxdr_encode_holder`, and `svcxdr_encode_testrply`. Exported-to-procedure-table functions include `nlmsvc_decode_void`, `nlmsvc_decode_testargs`, `nlmsvc_decode_lockargs`, `nlmsvc_decode_cancargs`, `nlmsvc_decode_unlockargs`, `nlmsvc_decode_res`, `nlmsvc_decode_reboot`, `nlmsvc_decode_shareargs`, `nlmsvc_decode_notify`, `nlmsvc_encode_void`, `nlmsvc_encode_testres`, `nlmsvc_encode_res`, and `nlmsvc_encode_shareres`.

## Control Flow

Decode functions consume fields in protocol order from `xdr_stream`: cookie, booleans, caller string, file handle, owner handle, svid, range, reclaim/state, share modes, or statd notify fields. `svcxdr_decode_lock` initializes a POSIX read lock by default, computes `fl_start`/`fl_end`, and callers set write or unlock type as needed. Encode functions write cookie/status pairs, optional conflicting holder data for denied TEST replies, and the share response sequence field.

## State and Persistence Behavior

The file owns no persistent state. Decoded strings and owner handles may point into the transient RPC receive buffer, while cookies and file handles are copied into request storage. VFS locks are initialized for later procedure-layer completion.

## Dependencies and Integration Points

It depends on SUNRPC XDR streams, NFSv2 file-handle size constants, `lockd.h`, `share.h`, `svcxdr.h`, and VFS lock initialization. Its functions are referenced by `svcproc.c` procedure descriptors.

## Risks and Edge Cases

NLM v1/v3 file handles are constrained to exactly `NFS2_FHSIZE`, not the protocol's larger generic opaque maximum. Offset conversion saturates to `NLM_OFFSET_MAX` on encode and treats zero or wrapped lengths as EOF on decode. Share-argument range checks are explicitly noted as missing in the original code. Truncated XDR input must fail without partially trusted state.

## Test Signals

Fuzz all decode routines with malformed/truncated XDR, max and zero cookies, invalid file-handle lengths, negative/overflowing ranges, and share mode values. Exercise TEST denied replies to validate holder encoding, EOF range encoding, and v1/v3 procedure-table xdr sizes.
