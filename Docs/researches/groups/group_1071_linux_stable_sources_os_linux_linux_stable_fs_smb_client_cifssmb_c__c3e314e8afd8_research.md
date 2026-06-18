# Group Research: group_1071_linux_stable_sources_os_linux_linux_stable_fs_smb_client_cifssmb_c__c3e314e8afd8

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux-stable/fs/smb/client/*`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifssmb.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/cifssmb.c

## Role

SMB1/CIFS PDU construction, send, reconnect, and response parsing layer for the Linux SMB client. This file implements most legacy CIFS/SMB1 wire operations exposed through the client operation tables: negotiate, tree connect, file open/read/write/lock/close, path operations, Trans2 metadata queries, NT transact security descriptor and IOCTL paths, DFS referrals, POSIX/Unix extension calls, and xattr/EA support.

## Main Operation Families

- Connection and request setup:
  - `cifs_reconnect_tcon()` gates sends through server/session/tree reconnect handling and returns `-EAGAIN` for stale handle-based operations that the caller must retry after reopening.
  - `small_smb_init()`, `__smb_init()`, `smb_init()`, and `smb_init_no_reconnect()` allocate request buffers, assemble SMB headers, and update per-tree send stats.
  - `validate_t2()` and `validate_ntransact()` perform common Trans2/NTTransact response bounds checks before parsing parameter/data areas.
- Negotiation and session/tree lifetime:
  - `CIFSSMBNegotiate()` sends SMB1 dialect negotiation, parses server capabilities, signing/security mode, max buffer/read/write sizes, and extended security blobs.
  - `CIFSTCon()`, `CIFSSMBTDis()`, `CIFSSMBLogoff()`, and `CIFSSMBEcho()` implement tree connect/disconnect, session logoff, and echo keepalive.
- Namespace mutation:
  - `CIFSSMBDelFile()`, `CIFSSMBRmDir()`, `CIFSSMBMkDir()`, `CIFSSMBRename()`, `CIFSUnixCreateSymLink()`, `CIFSUnixCreateHardLink()`, `CIFSCreateHardLink()`, and `CIFSPOSIXDelFile()` build pathname-oriented SMB1/Trans2 requests with ASCII or UTF-16 pathname conversion.
  - `CIFSSMBRenameOpenFile()` renames by file handle using `TRANS2_SET_FILE_INFORMATION`.
- Opens and I/O:
  - `CIFSPOSIXCreate()`, `SMBLegacyOpen()`, and `CIFS_open()` implement POSIX open, legacy `OPEN_ANDX`, and NT create.
  - `CIFSSMBRead()`, `cifs_async_readv()`, `CIFSSMBWrite()`, `cifs_async_writev()`, and `CIFSSMBWrite2()` implement sync and async SMB1 reads/writes, including large-file offsets, `CountHigh` correction, netfs completion, signature verification, and credit return.
- Locks and handle operations:
  - `cifs_lockv()`, `CIFSSMBLock()`, and `CIFSSMBPosixLock()` send Windows and POSIX byte-range lock requests.
  - `CIFSSMBClose()` and `CIFSSMBFlush()` close and flush server handles.
- Reparse and compression FSCTLs:
  - `cifs_query_reparse_point()` opens a path with `OPEN_REPARSE_POINT`, sends `FSCTL_GET_REPARSE_POINT`, validates response layout, and returns the reparse buffer.
  - `cifs_create_reparse_inode()` creates a placeholder object, optionally writes EAs, sends `FSCTL_SET_REPARSE_POINT`, then fetches inode info or deletes the placeholder on failure.
  - `CIFSSMB_set_compression()` sends `FSCTL_SET_COMPRESSION` for a file handle.
- Metadata query/set:
  - `SMBQueryInformation()`, `CIFSSMBQFileInfo()`, `CIFSSMBQPathInfo()`, `CIFSSMBUnixQFileInfo()`, `CIFSSMBUnixQPathInfo()`, and `CIFSGetSrvInodeNumber()` query legacy, NT, and Unix metadata.
  - `CIFSSMBSetEOF()`, `CIFSSMBSetFileSize()`, `SMBSetInformation()`, `CIFSSMBSetFileInfo()`, `CIFSSMBSetFileDisposition()`, `CIFSSMBSetPathInfo()`, `CIFSSMBUnixSetFileInfo()`, and `CIFSSMBUnixSetPathInfo()` update EOF/allocation, basic attributes, delete disposition, and Unix uid/gid/mode/time fields.
- ACLs, security descriptors, and EAs:
  - POSIX ACL support converts between CIFS ACL wire entries and Linux `struct posix_acl`.
  - `CIFSSMBGetCIFSACL()` and `CIFSSMBSetCIFSACL()` use NT transact security descriptor calls.
  - `CIFSSMBQAllEAs()` and `CIFSSMBSetEA()` implement query/list/set extended attributes through Trans2 EA info levels.
- Directory and filesystem queries:
  - `CIFSFindFirst()`, `CIFSFindNext()`, and `CIFSFindClose()` manage SMB1 directory search handles and network search buffers.
  - `CIFSGetDFSRefer()` sends `TRANS2_GET_DFS_REFERRAL` through IPC tree state.
  - `SMBOldQFSInfo()`, `CIFSSMBQFSInfo()`, `CIFSSMBQFSAttributeInfo()`, `CIFSSMBQFSDeviceInfo()`, `CIFSSMBQFSUnixInfo()`, `CIFSSMBSetFSUnixInfo()`, and `CIFSSMBQFSPosixInfo()` populate `kstatfs` and tree filesystem capability fields.

## Control Flow and Integration

Most public functions follow a repeatable pattern: initialize an SMB header, encode parameters and path/data payloads, call `SendReceive()`, `SendReceive2()`, `SendReceiveNoRsp()`, or `cifs_call_async()`, validate the response when one is expected, copy/convert wire data into CIFS or VFS structures, release the CIFS buffer, and retry on `-EAGAIN` only when the operation is path-based and safe to rebuild.

The file integrates with shared CIFS state in `struct cifs_ses`, `struct cifs_tcon`, `struct TCP_Server_Info`, `struct cifs_sb_info`, and `struct cifsFileInfo`. It relies on helpers from sibling files for header assembly, path conversion, DFS referral parsing, inode refresh, signature checking, credit accounting, xattr/reparse helpers, and netfs subrequest termination.

## State, Locking, and Lifetime

- Reconnect paths coordinate with `session_mutex`, `ses_lock`, `chan_lock`, `srv_lock`, `need_reconnect`, session status, and server TCP status.
- Async I/O callbacks own mid completion, netfs progress flags, request result propagation, mid release, and credit return.
- Search state owns a network response buffer across `FindFirst`/`FindNext`; `FindNext` frees the previous search buffer only after a replacement response is accepted.
- Response buffers from `SendReceive2()` are released through `free_rsp_buf()`, while normal CIFS request buffers use `cifs_buf_release()` or `cifs_small_buf_release()`.

## Validation and Risk Notes

The file contains many explicit bounds checks for Trans2 data offsets, byte counts, reparse buffers, EA list lengths, ACL sizes, read sizes, and filesystem info sizes. Remaining risk is typical for old SMB1 code: many routines manually compute byte counts, offsets, padding, and UTF-16 name lengths, so correctness depends on matching exact wire layouts. Several comments mark historical compatibility behavior and older-server workarounds, especially around information levels, Unix extensions, EA sizing, and handle-based retry behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/cifssmb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/compress.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/compress.c

## Role

SMB 3.1.1 client-side I/O compression support for outgoing SMB2 write messages and compression eligibility checks for SMB2 read/write traffic. It implements the policy layer around negotiated compression, share flags, compressibility heuristics, LZ77 compression, compression transform header construction, and fallback to uncompressed sending.

## Key Functions

- `should_compress()` decides whether a request should use SMB compression.
  - Requires a valid tree/session/server.
  - Requires negotiated server compression and `SMB2_SHAREFLAG_COMPRESS_DATA`.
  - Allows reads when share/server compression is enabled.
  - Allows writes only when the write length is at least `SMB_COMPRESS_MIN_LEN` and `is_compressible()` accepts the request iterator.
- `smb_compress()` compresses an SMB2 write request before sending.
  - Validates the request shape as a single `smb2_write_req` iovec.
  - Copies the original write payload out of the iterator into a temporary source buffer.
  - Allocates a destination buffer using `lz77_compressed_alloc_size()`.
  - Calls `lz77_compress()`.
  - On success, wraps the original SMB2 write header and compressed payload in `struct smb2_compression_hdr` and sends a three-iovec request.
  - On `-EMSGSIZE` or non-smaller output, falls back to the original uncompressed request.

## Compressibility Heuristic

The heuristics are derived from Btrfs compression sampling logic and operate on a sampled copy of the write iterator:

- `collect_sample()` copies 2 KiB chunks with 2 KiB gaps, up to a 4 MiB sample.
- `has_repeated_data()` accepts exact repeated halves early.
- `is_mostly_ascii()` treats a narrow byte alphabet as likely compressible.
- `calc_byte_distribution()` sorts byte buckets by count and classifies distribution as good, bad, or maybe.
- `has_low_entropy()` computes an integer Shannon-entropy approximation and rejects data above the threshold.

The heuristic deliberately avoids compressing data that looks random, encrypted, or unlikely to benefit from LZ77.

## Dependencies and Integration

Uses `struct smb_rqst`, `struct iov_iter`, and SMB2 headers from CIFS/SMB common headers. The actual compression engine is `lz77_compress()` from `compress/lz77.c`. The send path is abstracted behind `compress_send_fn`, allowing the caller to provide the normal SMB send function.

## Risk Notes

The compressor copies the full write payload before compression, so memory use scales with request size plus worst-case compressed allocation. The fallback behavior is conservative: failure to compress due to bad ratio sends the original request, while allocation and copy failures propagate errors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/compress.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/compress.h

## Role

Public CIFS client header for SMB 3.1.1 compression support. It defines compression header sizing constants, minimum compression size, the compressed-send callback type, compression entry points, algorithm validation, and disabled stubs for builds without `CONFIG_CIFS_COMPRESSION`.

## Key Definitions

- `SMB_COMPRESS_HDR_LEN` is the SMB2 compression transform header length excluding `OriginalPayloadSize`.
- `SMB_COMPRESS_PAYLOAD_HDR_LEN` is the chained payload header length excluding `OriginalPayloadSize`.
- `SMB_COMPRESS_MIN_LEN` is `PAGE_SIZE`; writes smaller than this are not considered for compression.
- `compress_send_fn` is the callback signature used by `smb_compress()` to send either compressed or fallback requests.

## API Surface

- `smb_compress(struct TCP_Server_Info *server, struct smb_rqst *rq, compress_send_fn send_fn)` compresses and sends an SMB request when supported.
- `should_compress(const struct cifs_tcon *tcon, const struct smb_rqst *rq)` evaluates negotiated capability, share flags, command type, size, and data compressibility.
- `smb_compress_alg_valid(__le16 alg, bool valid_none)` accepts `SMB3_COMPRESS_LZ77` and `SMB3_COMPRESS_PATTERN`, and accepts `SMB3_COMPRESS_NONE` only when the caller explicitly allows it.

## Build-Time Behavior

When `CONFIG_CIFS_COMPRESSION` is disabled, the header provides inline stubs: `smb_compress()` returns `-EOPNOTSUPP`, `should_compress()` returns `false`, and `smb_compress_alg_valid()` returns `-EOPNOTSUPP`.

## Research Notes

The header is intentionally narrow. It exposes only the policy/send entry points and validation helper; algorithm internals live under `compress/`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/compress.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/compress/lz77.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/compress/lz77.c

## Role

Plain LZ77 compressor implementation for SMB compression, following the MS-XCA plain LZ77 format. This file provides compression only; decompression is not implemented here.

## Algorithm Structure

- Compression parameters:
  - Maximum match distance: 8 KiB.
  - Hash table size: 32 Ki entries.
  - Minimum read/match seed size: 4 bytes.
  - Match extension step: 8 bytes.
  - Adaptive skip trigger: 4, increasing skip distance after repeated misses.
- `lz77_compress()`:
  - Verifies the destination allocation is at least `lz77_compressed_alloc_size(slen)`.
  - Allocates a zeroed hash table.
  - Reserves the first 4-byte flag word.
  - Scans the input using a rolling hash of 4-byte sequences.
  - Emits unmatched bytes as literals.
  - Emits back-reference matches when a prior hash entry is close enough and has the same 4-byte seed.
  - Finalizes trailing literals and the final flag word.
  - Returns 0 only if compressed output is smaller than input; otherwise returns `-EMSGSIZE`.

## Key Helpers

- `lz77_read8()`, `lz77_read32()`, `lz77_read64()` and matching write helpers perform unaligned little-endian-safe accesses.
- `lz77_match_len()` extends a match using 64-bit XOR and trailing-zero counting, with byte fallback at the tail.
- `lz77_encode_match()` encodes distance and length using the MS-XCA match format, including nibble-packed and extended length encodings.
- `lz77_encode_literals()` copies literal runs and maintains 32-bit flag groups.
- `lz77_hash()` maps 4-byte sequences into the fixed-size hash table.

## State and Memory

The compressor is stateless across calls. Each call allocates an `LZ77_HASH_SIZE` table with `kvcalloc()` and frees it before returning. The caller owns the source and destination buffers and must provide enough destination space for the no-bound-checking hot path.

## Integration

`compress.c` calls this function for outgoing SMB2 write compression and supplies the destination allocation size through `lz77_compressed_alloc_size()` from `lz77.h`.

## Risk Notes

The main loop intentionally avoids destination bound checks for performance and depends on the caller passing the worst-case allocation size. The function defends this with an initial `WARN_ON_ONCE()` and `-EINVAL` if `*dlen` is too small.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/compress/lz77.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/compress/lz77.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/compress/lz77.h

## Role

Header for the SMB client plain LZ77 compressor. It exposes the worst-case compressed allocation helper and the compressor function prototype.

## API Surface

- `lz77_compressed_alloc_size(const u32 size)` returns `size + (size >> 3) + 8`.
  - The extra space accounts for 4-byte flag metadata at the start, every 32 literals or matches, and the possible end flag.
  - The overprovisioned size lets `lz77_compress()` avoid per-write destination bounds checks in its hot loop.
- `lz77_compress(const void *src, const u32 slen, void *dst, u32 *dlen)` compresses a source buffer into a caller-provided destination buffer and updates `*dlen` with actual output size.

## Research Notes

This is a small performance contract header. Correct callers must allocate at least `lz77_compressed_alloc_size(input_size)` bytes before calling `lz77_compress()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/compress/lz77.h -->