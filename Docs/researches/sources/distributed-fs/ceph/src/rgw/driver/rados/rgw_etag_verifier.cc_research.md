# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_etag_verifier.cc

## Purpose
`rgw_etag_verifier.cc` implements a put-object data processor that recomputes ETags while object data is streamed. It verifies multisite-copied objects by reproducing either atomic-object MD5 ETags or multipart-upload ETags from object manifests.

## Important APIs, Types, And Functions
`create_etag_verifier()` decodes an `RGWObjManifest`, chooses `ETagVerifier_Atomic` for atomic objects, or constructs `ETagVerifier_MPU` with part offsets for MPU objects. For compressed sources it maps compressed manifest offsets back to original offsets using `RGWCompressionInfo::blocks`.

`ETagVerifier_Atomic::process()` updates a single MD5 hash for every bufferlist and passes data down the pipe. `calculate_etag()` finalizes that hash and hex-encodes it.

`ETagVerifier_MPU::process_end_of_MPU_part()` finalizes a part hash, feeds the raw MD5 digest into the MPU hash, restarts the part hash, and advances indexes. `process()` splits input that spans part boundaries and updates the appropriate hashes. `calculate_etag()` finalizes the last part, finalizes the MPU hash, and appends `-<parts>`.

## Control Flow
The verifier is inserted into the put pipeline before object data is written or passed to the next processor. Data chunks arrive with logical offsets. Atomic mode is linear. MPU mode tracks `cur_part_index` and `next_part_index`, detects boundary crossings, and updates per-part and aggregate hashes to match RGWCompleteMultipart behavior.

## State And Persistence Behavior
The verifier has no persistent state. It computes `calculated_etag` in memory and exposes it through the base class. It depends on the persisted source manifest and optional compression metadata to derive part boundaries.

## Dependencies And Integration Points
The file depends on `rgw_obj_manifest.h`, `rgw_putobj` data processors, Ceph MD5 crypto, compression metadata, and logging. It is related to dedup because both depend on accurate ETag and manifest interpretation, but it lives under `rgw::putobj`.

## Risks And Edge Cases
If manifest decode or rule lookup fails, verifier construction returns `-EIO`. If compressed offsets cannot be mapped exactly to compression blocks, verification is disabled by returning `-EIO`. MPU boundary logic is sensitive to off-by-one errors; the condition `logical_offset + in.length() + 1 == part_ofs[next_part_index]` deserves targeted tests because offsets are usually half-open ranges.

`process()` uses `in.c_str()` and assumes the bufferlist content is contiguous enough for the requested update. If fragmented bufferlists are possible in this pipe, callers or MD5 update semantics must make that safe.

## Test Signals
Tests should cover atomic ETag, multipart ETag with chunks aligned and crossing part boundaries, compressed offset remapping, malformed manifests, missing manifest rule, empty data, repeated `calculate_etag()` idempotence, and FIPS-allowed MD5 behavior.
