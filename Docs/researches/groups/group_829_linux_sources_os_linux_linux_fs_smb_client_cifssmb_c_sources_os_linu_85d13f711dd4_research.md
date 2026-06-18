# Group Research: group_829_linux_sources_os_linux_linux_fs_smb_client_cifssmb_c_sources_os_linu_85d13f711dd4

Scope checked against `Docs/research_subset_a.md`; all five listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifssmb.c -->
# File Research: sources/os/linux/linux/fs/smb/client/cifssmb.c

This is the SMB1/CIFS PDU construction and parsing implementation for the Linux CIFS client. It builds wire requests, sends them through the CIFS transport helpers, decodes SMB/Trans2/NT Transact responses, updates per-tree statistics, and coordinates retry/reconnect behavior.

Primary responsibilities:
- SMB1 negotiation, tree connect/disconnect, echo, and logoff.
- Path and handle operations: create/open, delete, mkdir/rmdir, rename, hard link, symlink, close, flush.
- Sync and async read/write using `SMB_COM_READ_ANDX` and `SMB_COM_WRITE_ANDX`, including NetFS subrequest completion callbacks.
- Byte-range locks, POSIX locks, oplock release signaling.
- Query/set metadata through legacy SMB, Trans2, NT Transact, Unix extensions, POSIX ACLs, CIFS ACLs, DFS referrals, reparse points, filesystem info, extended attributes.
- Conditional code for `CONFIG_CIFS_POSIX`, `CONFIG_FS_POSIX_ACL`, `CONFIG_CIFS_XATTR`, and DFS upcall support.

Important control flow:
- `cifs_reconnect_tcon()` is the gate before most tree-based operations. It waits for server reconnect, serializes session setup with `session_mutex`, can swap alternate passwords after auth failures, reconnects the tree, resets Unix caps, and returns `-EAGAIN` for handle-based commands that cannot safely reuse stale FIDs.
- `small_smb_init()`, `smb_init()`, `smb_init_no_reconnect()`, and `smb_init_nttransact()` are the main request-buffer constructors. They assemble SMB headers, assign stats, and choose small vs large CIFS buffers.
- Many request routines follow the pattern `init -> encode pathname/params/data -> SendReceive/SendReceive2/NoRsp -> validate response -> copy out -> release buffer -> retry on -EAGAIN when path-based`.

Response validation and safety:
- `validate_t2()` checks Trans2 word count, parameter/data offsets, ByteCount, and negotiated buffer bounds before response decoding.
- `validate_ntransact()` bounds-checks NT Transact parameter/data regions against the SMB ByteCount area.
- Read paths check returned data length against `CIFSMaxBufSize` and requested count.
- Reparse point parsing validates data offsets, setup count, returned data length, reparse buffer length, and returns the response buffer to the caller on success.
- EA listing walks `fealist` entries with explicit list-length and end-of-SMB checks before copying names or values.

Notable data handling:
- Pathnames are encoded as UTF-16 when `SMBFLG2_UNICODE` is set; otherwise `copy_path_name()`/ASCII paths are used. Most conversions cap at `PATH_MAX` and use `cifs_remap()`.
- File IDs remain little-endian on the wire (`netfid`/`Fid` comments call this out repeatedly).
- Large-file capability changes read/write word counts and high-offset fields.
- Legacy paths support old servers via `SMBQueryInformation()`, `SMBOldQFSInfo()`, and `SMBSetInformation()`.
- Unix extension paths map Unix basic info, symlink/hardlink, POSIX create, POSIX locks, POSIX filesystem info, Unix caps, and POSIX ACL wire formats.

NetFS/async behavior:
- `cifs_async_readv()` and `cifs_async_writev()` submit async SMB1 read/write requests.
- `cifs_readv_callback()` verifies signatures when needed, accounts bytes, sets NetFS progress/EOF/retry flags, releases credits, terminates the read subrequest, and releases the MID.
- `cifs_writev_callback()` validates the response, masks bad OS/2 `CountHigh` values, maps short writes to `-ENOSPC`, sets progress, terminates the write subrequest, and restores credits.

Resource and retry notes:
- Path-based operations commonly retry internally on `-EAGAIN`; handle-based operations generally return to the caller because a reconnect invalidates the FID.
- Close/find-close/tree-disconnect/logoff suppress some reconnect errors because the server-side object is already gone after a dead session.
- Buffer ownership varies: most functions release their SMB buffer before return; search operations deliberately retain the response buffer in `cifs_search_info`; reparse query returns the response buffer to the caller.
- Care point: a few post-allocation `tcon->ses->server == NULL` checks in read/write paths return without local release in this file; callers and future edits should audit those lifetimes before refactoring.

Open issues embedded in comments:
- Lock reclaim after reconnect is still questioned.
- Several `BB/FIXME` notes ask for tighter max data sizing from session state, stronger buffer-overrun checks, better Trans2 EA validation, fallback logic for unsupported Unix search levels, and ACL overflow checks.
- Some legacy open response fields and timestamp conversions are intentionally incomplete or approximate.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/cifssmb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/compress.c -->
# File Research: sources/os/linux/linux/fs/smb/client/compress.c

This file implements SMB 3.1.1 client-side send compression support when `CONFIG_CIFS_COMPRESSION` is enabled. It currently compresses write payloads with plain LZ77 and can request compressed reads when negotiated/share policy allow it.

Main pieces:
- Compressibility heuristic helpers derived from Btrfs compression logic.
- `should_compress()` decides whether a read/write SMB2 request should use compression.
- `smb_compress()` copies a write payload, LZ77-compresses it, wraps it in an SMB2 compression transform header, and invokes the supplied send function.

Compressibility heuristic:
- `collect_sample()` copies 2 KiB chunks with 2 KiB gaps from an `iov_iter`, capped at a 4 MiB sample window.
- `has_repeated_data()` accepts obvious repeated halves early.
- `is_mostly_ascii()` treats low distinct-byte-count ASCII-like data as compressible.
- `calc_byte_distribution()` classifies sorted byte-frequency buckets as bad/good/maybe.
- `has_low_entropy()` computes a Shannon-style integer entropy estimate and accepts only below threshold.
- Allocation/copy failures warn once and fail closed by returning not compressible.

Compression gating:
- Requires non-null `tcon`, session, server.
- Requires `server->compression.enabled`.
- Requires share flag `SMB2_SHAREFLAG_COMPRESS_DATA`.
- For writes, requires `Length >= SMB_COMPRESS_MIN_LEN` and `is_compressible(&rq->rq_iter)`.
- For reads, returns true if the command is `SMB2_READ` after negotiation/share checks.

`sm渲b_compress()` behavior:
- Validates the request is a single `smb2_write_req` header vector.
- Copies the original payload from `rq_iter` into a temporary source buffer without mutating the original iterator.
- Allocates destination size using `lz77_compressed_alloc_size()`.
- On successful and smaller LZ77 output, sends three vectors: compression transform header, original SMB2 write request header, compressed payload.
- If compression fails with `-EMSGSIZE` or output is not smaller, sends the original request uncompressed.
- Frees temporary buffers on all normal exits.

Dependencies:
- Uses SMB2 wire structures from `../common/smb2pdu.h`, CIFS globals/prototypes, and `compress/lz77.h`.
- The caller supplies `compress_send_fn`, keeping transport sending outside this file.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/compress.h -->
# File Research: sources/os/linux/linux/fs/smb/client/compress.h

This header defines the public compression interface for the CIFS/SMB client.

Key definitions:
- `SMB_COMPRESS_HDR_LEN` is 16, excluding `OriginalPayloadSize`.
- `SMB_COMPRESS_PAYLOAD_HDR_LEN` is 8, excluding `OriginalPayloadSize`.
- `SMB_COMPRESS_MIN_LEN` is `PAGE_SIZE`.
- `compress_send_fn` is the callback type used by `smb_compress()` to send either transformed or original requests.

When `CONFIG_CIFS_COMPRESSION` is enabled:
- Exposes `smb_compress()`.
- Exposes `should_compress()`.
- Provides `smb_compress_alg_valid()`, accepting `SMB3_COMPRESS_LZ77` and `SMB3_COMPRESS_PATTERN`; `SMB3_COMPRESS_NONE` is conditionally valid based on the caller’s `valid_none` argument.

When compression is disabled:
- `smb_compress()` returns `-EOPNOTSUPP`.
- `should_compress()` returns false.
- `smb_compress_alg_valid()` returns `-EOPNOTSUPP`.

Important semantic note:
- The header documents that `SMB3_COMPRESS_NONE` is not valid during protocol negotiation, even though some callers may allow it in non-negotiation contexts.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/compress.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/compress/lz77.c -->
# File Research: sources/os/linux/linux/fs/smb/client/compress/lz77.c

This file implements the MS-XCA plain LZ77 compressor used by SMB compression.

Compression parameters:
- Maximum match distance: 8 KiB.
- Hash table: 32 Ki entries (`LZ77_HASH_LOG == 15`).
- Minimum/hash read step: 4 bytes.
- Match extension step: 8 bytes.
- Adaptive skip trigger: 4, increasing skip distance after repeated misses.
- Flag groups contain 32 literals/matches.

Core helpers:
- Unaligned little-endian read/write wrappers for 8/16/32/64-bit access.
- `lz77_match_len()` compares 8 bytes at a time, uses trailing-zero count to find first differing byte, then falls back to byte comparison near the end.
- `lz77_encode_match()` emits MS-XCA match tokens with distance, short/extended length, nibble packing, 8-bit, 16-bit, or 32-bit length extension.
- `lz77_encode_literals()` copies literal runs and flushes 32-bit flag words as groups fill.
- `lz77_hash()` hashes 4-byte sequences for match lookup.

`lz77_compress()` flow:
- Requires caller-provided `*dlen` to be at least `lz77_compressed_alloc_size(slen)`; warns and returns `-EINVAL` otherwise.
- Allocates a zeroed hash table with `kvcalloc`.
- Seeds the hash table while avoiding a false first-iteration match.
- Main loop searches for in-window matching 4-byte sequences, using adaptive skipping for speed.
- On match, flushes pending literals, computes full match length, encodes match, advances anchor, updates flags, and continues.
- On exit, flushes remaining literals, writes final padded flag word, stores compressed length, frees hash table.
- Returns `0` only if compressed output is smaller than source; otherwise returns `-EMSGSIZE`.

Performance/safety assumptions:
- Destination bound checks are intentionally omitted inside the hot loop because the caller is required to allocate the worst-case size.
- The code comments warn that reordering the hot path can significantly hurt performance.
- All source reads are limited by `rlim = end - 8` for fast match extension, with byte fallback at tail.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/compress/lz77.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/compress/lz77.h -->
# File Research: sources/os/linux/linux/fs/smb/client/compress/lz77.h

This header exposes the plain LZ77 compressor.

Public API:
- `lz77_compressed_alloc_size(size)` returns `size + (size >> 3) + 8`.
- `lz77_compress(src, slen, dst, dlen)` compresses source into destination and updates `*dlen`.

Allocation rationale:
- LZ77 metadata writes a 4-byte flag at the start, every 32 literals/matches, and possibly at stream end.
- Worst-case all-literal output needs roughly `size >> 3` extra bytes plus 8 bytes.
- The overprovisioning is deliberate so `lz77_compress()` can avoid destination bound checks in its main loop while remaining safe if compression is ineffective.

Contract:
- Callers must allocate at least `lz77_compressed_alloc_size(slen)` bytes for `dst` and pass that capacity in `*dlen`.
- The compressor reports success only when compressed output is smaller than input.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/compress/lz77.h -->