<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/compress.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/compress.h

Purpose: declares the SMB client message-compression API and constants for SMB 3.1.1 compression support. It centralizes the compile-time `CONFIG_CIFS_COMPRESSION` boundary so callers can invoke compression helpers without open-coding feature guards.

Important APIs, types, and functions: defines `SMB_COMPRESS_HDR_LEN`, `SMB_COMPRESS_PAYLOAD_HDR_LEN`, and `SMB_COMPRESS_MIN_LEN` (`PAGE_SIZE`). Under `CONFIG_CIFS_COMPRESSION`, it defines `compress_send_fn`, declares `smb_compress()` and `should_compress()`, and provides `smb_compress_alg_valid(__le16 alg, bool valid_none)`. Supported negotiated algorithms in this client-side check are `SMB3_COMPRESS_LZ77` and `SMB3_COMPRESS_PATTERN`; `SMB3_COMPRESS_NONE` is conditionally accepted only when the caller explicitly allows it. When compression is disabled at build time, inline stubs return `-EOPNOTSUPP` or `false`.

Control flow: callers use `should_compress()` to decide whether a request or response path is eligible, then use `smb_compress()` to wrap a write request before send. Negotiation parsing can use `smb_compress_alg_valid()` to reject unsupported or protocol-invalid algorithms while optionally accepting `NONE` in contexts where a sentinel value is legal.

State and persistence behavior: the header stores no state. Its constants affect runtime behavior by defining the minimum write length considered for compression and by exposing transform header sizing assumptions. The disabled stubs make compression a no-op capability at runtime while preserving build compatibility.

Dependencies and integration points: includes Linux `uio`/kernel types, common SMB2 PDU definitions for algorithm constants, and CIFS global types for `TCP_Server_Info`, `cifs_tcon`, and `smb_rqst`. It is included by transport and SMB2 PDU code as the boundary between generic send logic and the compression implementation.

Risks: `smb_compress_alg_valid()` supports LZ77 and PATTERN but `compress.c` currently emits LZ77 for outbound write compression; callers must not assume every valid negotiated algorithm has a full local compressor/decompressor path here. The non-compression stub for `smb_compress_alg_valid()` returns an `int` error value despite the enabled helper being used as boolean-like truth, so disabled-build callers should treat it as unavailable rather than a normal validator. Header-length constants omit `OriginalPayloadSize` by design and must stay synchronized with the protocol structs.

Test signals: build coverage with `CONFIG_CIFS_COMPRESSION=y` and disabled; negotiation tests for LZ77, PATTERN, NONE-valid, NONE-invalid, and unsupported algorithms; call-site tests that disabled builds fall back cleanly; and transform header sizing assertions against the SMB2 compression structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/compress.h -->
