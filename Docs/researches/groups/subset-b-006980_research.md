# subset-b-006980 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/jwt-cpp/jwt.h -->
# sources/distributed-fs/ceph/src/rgw/jwt-cpp/jwt.h

## Purpose
This header is Ceph RGW's vendored, header-only JWT implementation. It decodes, builds, signs, and verifies JSON Web Tokens using picojson for JSON, a local base64url helper, and OpenSSL for HMAC, RSA, ECDSA, and RSA-PSS algorithms. It is a security-sensitive dependency for RGW code paths that accept or issue JWT-like credentials.

## Important APIs, types, and functions
- Exception types: `signature_verification_exception`, `signature_generation_exception`, `rsa_exception`, `ecdsa_exception`, and `token_verification_exception` distinguish crypto setup, signing, and verification failures.
- `helper::extract_pubkey_from_cert()`, `load_public_key_from_string()`, and `load_private_key_from_string()` wrap PEM/certificate BIO handling and produce OpenSSL key objects.
- `jwt::algorithm` provides `none`, `hmacsha` with `hs256/hs384/hs512`, `rsa` with `rs256/rs384/rs512`, `ecdsa` with `es256/es384/es512`, and `pss` with `ps256/ps384/ps512`.
- `jwt::claim` wraps `picojson::value` and exposes typed conversion to string, int64 date, bool, double, array, object, and string set.
- `jwt::payload`, `jwt::header`, and `jwt::decoded_jwt` expose standard JWT claims and raw base64/decoded token parts.
- `jwt::builder` builds JSON header/payload maps and signs compact JWT strings.
- `jwt::verifier<Clock>` verifies the declared algorithm, signature, registered claims, audience membership, and time claims.

## Control flow
`decoded_jwt` splits the token on two dots, pads each base64url segment, decodes header/payload/signature, parses header and payload as JSON objects, and stores claims in unordered maps. `builder::sign()` constructs JSON objects, injects `alg`, serializes via picojson, base64url encodes without padding, signs `header.payload`, and appends the encoded signature. `verifier::verify()` reconstructs the signed data, selects an explicitly allowed algorithm by header `alg`, verifies the signature, checks exp/iat/nbf against the injected clock and leeway, then checks required claims and audience.

## State and persistence behavior
The header has no durable persistence. Runtime state is held in token strings, claim maps, OpenSSL key handles, and verifier allowed-algorithm maps. Crypto key material is copied into strings and OpenSSL objects for the lifetime of algorithm instances.

## Dependencies and integration points
The file depends on Ceph's vendored `picojson/picojson.h`, `base.h`, `rgw/rgw_b64.h`, STL containers/chrono, and OpenSSL EVP/HMAC/PEM/EC/RSA/BIGNUM APIs. It includes compatibility branches for OpenSSL 1.0 style context and ECDSA accessors. RGW integrations should construct a verifier with only expected algorithms; algorithm confusion protection depends on the caller configuring `allow_algorithm()`.

## Risks and edge cases
- `algorithm::none` is available; accepting it is safe only if callers never allow it for untrusted tokens.
- RSA JWK modulus/exponent support builds an `EVP_PKEY` from base64url strings; padding and malformed input need targeted tests.
- HMAC comparison avoids early exit but is not a dedicated constant-time primitive.
- ECDSA verification assumes the compact `r || s` signature format and does not explicitly reject odd or unexpected signature lengths before splitting.
- Leeway setters encode seconds as dates in `claims`; the verify path converts those dates back to seconds. This works by convention but is easy to misuse if claims are inspected as real expected time claims.
- `parse_claims()` assumes parsed JSON is an object before iterating `val.get<picojson::object>()`.

## Test signals
Useful tests should cover valid and invalid HS/RS/ES/PS tokens, wrong algorithm rejection, tampered signature rejection, PEM and certificate key loading, JWK modulus/exponent RSA verification, exp/iat/nbf leeway boundaries with a fake clock, string and array audience forms, malformed compact-token structure, invalid base64url, non-object JSON, and explicit rejection of `none` unless intentionally allowed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/jwt-cpp/jwt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/librgw.cc -->
# sources/distributed-fs/ceph/src/rgw/librgw.cc

## Purpose
This source file exposes the C ABI entry points for embedding RGW as `librgw`. It initializes the singleton RGW library object and returns a retained `CephContext` handle to C callers, then shuts the library down and releases the context.

## Important APIs, types, and functions
- Namespace state: `rgw::global_stop`, `rgw::librgw_mtx`, and static `RGWLib rgwlib`.
- `librgw_create(librgw_t* rgw, int argc, char **argv)` initializes `g_rgwlib`, optionally parses the last argument as a whitespace-split argument bundle, calls `rgwlib.init(args)`, and stores `g_ceph_context->get()` into the caller output.
- `librgw_shutdown(librgw_t rgw)` casts the opaque handle to `CephContext*`, calls `rgwlib.stop()`, logs final shutdown, and releases the context with `put()`.

## Control flow
Initialization is guarded by `g_ceph_context`. If no context exists, the mutex serializes the second check and `rgwlib.init()`. The last non-zero command-line argument can be split into multiple arguments before appending to the normal `argv_to_vec()` result. Shutdown is unconditional for the supplied handle.

## State and persistence behavior
The file manages process-global state rather than persistent data: `g_rgwlib`, `g_ceph_context`, the static RGW library instance, and CephContext reference counts. No disk or RADOS objects are written here.

## Dependencies and integration points
It includes the public `include/rados/librgw.h` C header, Ceph argument parsing and context headers, and `rgw_lib.h`. It is the boundary between external C/C++ consumers and RGW's internal singleton service.

## Risks and edge cases
- `librgw_create()` assigns `*rgw = g_ceph_context->get()` even if initialization failed after leaving `g_ceph_context` null; callers rely on `rgwlib.init()` behavior to establish context.
- Only initialization is mutex-protected. Concurrent shutdown/create interactions depend on broader RGW library semantics.
- Splitting only the final argument is a compatibility behavior that can surprise callers if paths or values contain spaces.

## Test signals
Tests should exercise successful create/shutdown, repeated create calls, failing initialization paths, final-argument splitting, reference-count balance under repeated use, and concurrent create attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/librgw.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/madler/crc32iscsi.c -->
# sources/distributed-fs/ceph/src/rgw/madler/crc32iscsi.c

## Purpose
This C file implements CRC-32C/iSCSI using Mark Adler style generated tables. It provides bit-at-a-time, byte-table, word-slicing, remainder-bit, and CRC-combine routines for the reflected polynomial `0x82f63b78`.

## Important APIs, types, and functions
- `crc32iscsi_bit()` computes the CRC one bit at a time and complements before/after processing.
- `crc32iscsi_rem()` extends a CRC with a partial trailing byte of `bits` low-order bits.
- `crc32iscsi_byte()` uses `table_word[0]` as a byte lookup table.
- `crc32iscsi_word()` uses slicing-by-8 lookup tables and 64-bit loads for throughput.
- `crc32iscsi_comb()` combines two CRCs with `len2` bytes in the second message using `multmodp()` and `x8nmodp()`.

## Control flow
The bit and remainder paths update the reflected CRC by shifting right and conditionally xoring the iSCSI polynomial. The byte path folds each byte through `table_byte[(crc ^ data[i]) & 0xff]`. The word path first processes bytes until the input pointer is 8-byte aligned, processes `len >> 3` little-endian 64-bit words using eight table rows, then processes the tail bytes. Combine computes the polynomial multiplier for `x^(8*len2)` and applies it to `crc1`, then xors `crc2`.

## State and persistence behavior
All tables are static constants and all CRC state is passed by value. There is no persistence, allocation, or global mutable state.

## Dependencies and integration points
The file includes `crc32iscsi.h`, which supplies `<stddef.h>` and `<stdint.h>`. It is suitable for RGW checksum code that needs CRC-32C semantics and can choose slower or faster routines depending on platform assumptions.

## Risks and edge cases
- `crc32iscsi_word()` explicitly assumes little-endian integer storage and performs casted 64-bit loads after alignment; portability depends on architecture and strict-aliasing/compiler behavior.
- `crc32iscsi_rem()` masks with `(1U << bits) - 1`; callers must keep `bits` in `0..8` as documented.
- Passing `NULL` returns zero, ignoring the supplied prior CRC. That encodes "CRC of zero bytes" but can hide caller mistakes.
- Table corruption or mismatch would silently produce incompatible checksums, so golden-vector tests are important.

## Test signals
Compare bit, byte, and word outputs for the same data; verify standard CRC-32C check values such as `"123456789"`; test incremental update and `crc32iscsi_comb()` against concatenated buffers; test NULL and zero-length behavior; test all `bits` values in `crc32iscsi_rem()`; and run on little-endian CI with sanitizers if possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/madler/crc32iscsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/madler/crc32iscsi.h -->
# sources/distributed-fs/ceph/src/rgw/madler/crc32iscsi.h

## Purpose
This header declares the public CRC-32C/iSCSI routines implemented in `crc32iscsi.c`.

## Important APIs, types, and functions
It includes `<stddef.h>` and `<stdint.h>` and declares `crc32iscsi_bit()`, `crc32iscsi_rem()`, `crc32iscsi_byte()`, `crc32iscsi_word()`, and `crc32iscsi_comb()`.

## Control flow
There is no executable control flow in the header. The comments define the contract: the update routines apply bytes at `mem` to a prior CRC, `NULL` returns the initial CRC of zero bytes, `_rem` handles a non-byte-aligned suffix, and `_comb` combines CRCs for concatenated data.

## State and persistence behavior
No state or persistence is declared.

## Dependencies and integration points
Consumers include this header when they need CRC-32C/iSCSI checksums. The API uses C integer types and is independent of Ceph C++ classes.

## Risks and edge cases
The header documents that `bits` must be `0..8` but does not enforce it. It also does not document the little-endian assumption of the `_word` implementation, so callers may need platform gating.

## Test signals
Compile C and C++ users against the header, validate ABI-visible function names, and run the implementation's golden-vector tests for every declared routine.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/madler/crc32iscsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/madler/crc32iso_hdlc.c -->
# sources/distributed-fs/ceph/src/rgw/madler/crc32iso_hdlc.c

## Purpose
This C file implements reflected CRC-32/ISO-HDLC using generated lookup tables. It mirrors the iSCSI implementation shape but uses polynomial `0xedb88320` and exports `crc32iso_hdlc_*` symbols.

## Important APIs, types, and functions
- `crc32iso_hdlc_bit()` provides the reference bitwise algorithm.
- `crc32iso_hdlc_rem()` processes a partial final byte.
- `crc32iso_hdlc_byte()` performs table-driven byte updates.
- `crc32iso_hdlc_word()` performs slicing-by-8 updates over aligned little-endian 64-bit words.
- `crc32iso_hdlc_comb()` combines two CRCs over concatenated messages.

## Control flow
The implementation complements the prior CRC in the bit/rem paths, shifts reflected bits right, and xors with `0xedb88320` on set low bits. The byte path advances through `table_word[0]`; the word path aligns the pointer, folds 64-bit words through eight table rows, and handles the remaining tail. `multmodp()` and `x8nmodp()` implement polynomial multiplication for combining.

## State and persistence behavior
There is no mutable state or persistence. Lookup and combination tables are static constants.

## Dependencies and integration points
The file includes `crc32iso_hdlc.h` only. It is an RGW-local checksum utility and can be linked into code needing the ISO-HDLC/standard ZIP/Ethernet CRC-32 flavor.

## Risks and edge cases
- `_word` assumes little-endian storage and uses raw 64-bit loads.
- `_rem` depends on valid `bits` input.
- `NULL` input returning zero is documented but may mask misuse.
- Because CRC variants are easy to confuse, tests must distinguish ISO-HDLC from iSCSI/CRC-32C with known check values.

## Test signals
Verify `"123456789"` against the CRC-32/ISO-HDLC check value, compare bit/byte/word equality across sizes and alignments, test combine versus concatenation, test zero-length and NULL behavior, and include partial-bit tests for `_rem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/madler/crc32iso_hdlc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/madler/crc32iso_hdlc.h -->
# sources/distributed-fs/ceph/src/rgw/madler/crc32iso_hdlc.h

## Purpose
This header declares the public reflected CRC-32/ISO-HDLC routines implemented in `crc32iso_hdlc.c`.

## Important APIs, types, and functions
It includes `<stddef.h>` and `<stdint.h>` and declares `crc32iso_hdlc_bit()`, `crc32iso_hdlc_rem()`, `crc32iso_hdlc_byte()`, `crc32iso_hdlc_word()`, and `crc32iso_hdlc_comb()`.

## Control flow
The header has no executable control flow. Its comments define the same contract as the other madler CRC headers: update a prior CRC, return the zero-byte initial CRC for `NULL`, process partial low bits with `_rem`, and combine two CRCs with `_comb`.

## State and persistence behavior
No state or persistence is declared.

## Dependencies and integration points
This is a C API for RGW or utility callers needing standard CRC-32/ISO-HDLC. The interface is independent of Ceph object types.

## Risks and edge cases
`bits` bounds and `_word` platform suitability are not enforced in the header. The function names are the main guard against accidentally using the wrong CRC-32 variant.

## Test signals
Header-level checks should verify C/C++ compilation and symbol availability; implementation tests should validate known ISO-HDLC vectors and parity across bit, byte, word, remainder, and combine APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/madler/crc32iso_hdlc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/madler/crc64nvme.c -->
# sources/distributed-fs/ceph/src/rgw/madler/crc64nvme.c

## Purpose
This C file implements CRC-64/NVME with generated tables and the same update/combine structure as the 32-bit madler CRC files. It uses reflected polynomial `0x9a6c9329ac4bc9b5`.

## Important APIs, types, and functions
- `crc64nvme_bit()` is the bitwise reference update.
- `crc64nvme_rem()` handles a partial final byte.
- `crc64nvme_byte()` is table-driven per byte.
- `crc64nvme_word()` is slicing-by-8 over 64-bit words.
- `crc64nvme_comb()` combines CRCs for message concatenation using `multmodp()` and `x8nmodp()`.

## Control flow
The bit/rem paths complement the CRC, consume reflected bits by shifting right, and xor the NVME polynomial on set low bits. The byte path indexes the first table row. The word path processes leading bytes until 8-byte alignment, folds aligned 64-bit words through table rows 7..0, and then handles the tail. The combine path computes the x-power multiplier for `len2` bytes and xors with `crc2`.

## State and persistence behavior
The file uses static constant tables only. All CRC values are caller-owned values; there is no allocation, mutation of global state, or persistence.

## Dependencies and integration points
It includes `crc64nvme.h` for fixed-width integer declarations. It integrates with code paths that need NVMe-style 64-bit data integrity checks, including object/checksum handling in RGW where this variant is configured.

## Risks and edge cases
- `_word` assumes little-endian integer layout.
- The partial-bit mask uses `1U << bits`; callers must keep `bits` in range despite the 64-bit CRC width.
- Standard CRC-64 variants are often confused; the NVME polynomial must be tested independently from ECMA or ISO variants.
- Very large `len2` combine cases depend on `uintmax_t` width and table exponent cycling.

## Test signals
Use CRC-64/NVME golden vectors, compare bit/byte/word routines for varied alignment and lengths, verify `crc64nvme_comb()` against concatenated buffers, test zero-length and NULL behavior, and include large `len2` combination tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/madler/crc64nvme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/madler/crc64nvme.h -->
# sources/distributed-fs/ceph/src/rgw/madler/crc64nvme.h

## Purpose
This header declares the public CRC-64/NVME routines implemented in `crc64nvme.c`.

## Important APIs, types, and functions
It includes `<stddef.h>` and `<stdint.h>` and declares `crc64nvme_bit()`, `crc64nvme_rem()`, `crc64nvme_byte()`, `crc64nvme_word()`, and `crc64nvme_comb()`.

## Control flow
There is no executable control flow. Comments specify byte update behavior, `NULL` behavior, partial-bit handling, and CRC combination semantics.

## State and persistence behavior
No state or persistence is declared.

## Dependencies and integration points
This is a small C ABI header for code that needs CRC-64/NVME. It does not expose Ceph-specific types.

## Risks and edge cases
The header does not enforce the documented `bits` range or advertise the implementation's little-endian fast-path assumption. Users should select `_byte` or platform-gate `_word` on non-little-endian targets.

## Test signals
Compile users against the declarations and run implementation tests for known NVME CRC-64 vectors, parity among update variants, partial-bit behavior, and combine behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/madler/crc64nvme.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/picojson/picojson.h -->
# sources/distributed-fs/ceph/src/rgw/picojson/picojson.h

## Purpose
This is a vendored single-header JSON parser/serializer. RGW's JWT code enables `PICOJSON_USE_INT64` before including it so numeric date claims can remain integer values. The header provides a lightweight JSON value tree, serialization, stream operators, and recursive-descent parsing.

## Important APIs, types, and functions
- `picojson::value` stores one of null, bool, double, string, array, object, and optionally int64.
- `picojson::array` and `picojson::object` alias `std::vector<value>` and `std::map<std::string, value>`.
- `value::is<T>()`, `get<T>()`, `set<T>()`, `contains()`, `evaluate_as_boolean()`, `to_str()`, and `serialize()` are the main value APIs.
- Parser helpers include `input<Iter>`, `_parse_string()`, `_parse_codepoint()`, `_parse_array()`, `_parse_object()`, `_parse_number()`, and `_parse()`.
- Parse contexts include `default_parse_context`, `null_parse_context`, and `deny_parse_context`.
- Top-level `parse()` overloads parse from iterators, strings, and streams; stream operators use `get_last_error()`/`set_last_error()`.

## Control flow
`parse()` wraps input iterators in `input`, skips whitespace, dispatches by the next character, recursively parses arrays/objects, decodes strings including unicode surrogate pairs, parses numbers with `strtoimax` first when int64 support is enabled, and falls back to `strtod`. Serialization dispatches by type, escapes string control characters, optionally pretty-prints indentation, and emits locale-normalized numeric text.

## State and persistence behavior
`value` owns heap-allocated strings, arrays, and objects through a manual union plus `clear()`, copy/swap assignment, and optional move operations. There is no durable persistence. Missing array/object lookups return references to static null values, and the stream error API uses a static string.

## Dependencies and integration points
The header depends only on the C/C++ standard library and optional locale support. It is included by `jwt-cpp/jwt.h` and can be configured by macros such as `PICOJSON_USE_INT64`, `PICOJSON_USE_RVALUE_REFERENCE`, `PICOJSON_USE_LOCALE`, `PICOJSON_NOEXCEPT`, and `PICOJSON_ASSERT`.

## Risks and edge cases
- Manual union storage and static null references require care: non-const missing `get()` returns a static mutable null value.
- Deeply nested JSON can recurse until stack exhaustion.
- `parse(value&, const std::string&)` does not require full consumption of trailing non-whitespace unless callers inspect the returned iterator through the lower-level overload.
- Locale-aware parsing/printing can be surprising in multi-threaded programs that mutate process locale.
- Duplicate object keys overwrite earlier values through `o[key]`.
- Number parsing with int64 enabled changes type behavior; `is<double>()` can be true for int64 and `get<double>()` converts the value to number type.

## Test signals
Tests should cover valid/invalid JSON, full-consumption expectations, unicode escapes and surrogate errors, control-character escaping, int64 boundaries, floating special-value rejection, duplicate keys, deep nesting limits, stream failbit behavior, pretty serialization, and JWT claim parsing for objects, arrays, strings, and integer dates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/picojson/picojson.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/radosgw-admin/orphan.cc -->
# sources/distributed-fs/ceph/src/rgw/radosgw-admin/orphan.cc

## Purpose
This source implements RGW admin orphan-object tooling. `RGWOrphanSearch` builds temporary shard indexes of all candidate RADOS objects, all bucket instances, and all objects reachable from bucket indexes/manifests, then reports pool objects that appear unlinked and stale. `RGWRadosList` lists RADOS object IDs reachable from buckets, including manifest parts, DLO/SLO references, versions, and incomplete multipart uploads.

## Important APIs, types, and functions
- `obj_fingerprint()` normalizes raw RGW object IDs by bucket marker and logical object key, stripping namespace/suffix detail for comparison.
- `RGWOrphanStore::{init,read_job,write_job,remove_job,list_jobs,store_entries,read_entries}` persists job state and shard entries in the zone log pool omap.
- `RGWOrphanSearch::init()` loads or creates a job, sets defaults, and names per-shard temporary index objects.
- `build_all_oids_index()` scans every namespace in the target data pool and records non-head object IDs by fingerprint shard.
- `build_buckets_instance_index()` scans metadata section `bucket.instance`.
- `build_linked_oids_for_bucket()` lists bucket index entries, stats objects asynchronously, reads manifests, and records referenced raw objects.
- `build_linked_oids_index()` iterates bucket-instance shard omaps and records linked object fingerprints.
- `compare_oid_indexes()` walks all-vs-linked shard omaps and prints `leaked:` objects after an mtime stale threshold.
- `run()` advances the persisted stage machine; `finish()` removes temporary indexes and job state.
- `RGWRadosList::{run,process_bucket,handle_stat_result,do_incomplete_multipart}` prints reachable RADOS object IDs from bucket traversal.

## Control flow
Orphan search starts by opening the log pool and loading job state. A new job begins at `INIT`, then `run()` falls through stages after each successful save: list pool objects, list bucket instances, iterate bucket indexes to build linked-object indexes, then compare. Pool listing skips unidentified object names and head objects because heads are mutable and cleanup would race with normal object lifecycle. Bucket traversal skips stale bucket instances and buckets under resharding, lists versions with namespace enforcement disabled, avoids stats for small head-only objects unless detailed mode is enabled, and caps concurrent async stat operations by `max_concurrent_ios`.

`compare_oid_indexes()` creates one `OMAPReader` per all/linked shard pair. For each all-object key it computes a fingerprint, advances the linked reader while keys compare lower, and treats absence from linked as a potential leak. It re-stats the data object and suppresses objects newer than `start_time - stale_secs`.

`RGWRadosList` starts from a bucket or all buckets. It keeps a process map of whole buckets, prefixes, and exact keys discovered through DLO/SLO manifests. `process_bucket()` lists bucket index entries, handles versioned heads, stats objects, and prints raw manifest locations. In normal output mode it also lists incomplete multipart parts after the initial bucket traversal; when field-separator mode is enabled it includes bucket/object names and skips incomplete multipart post-processing.

## State and persistence behavior
Durable state lives in the log pool object `orphan.index`, keyed by job name, as encoded `RGWOrphanSearchState`. Temporary shard omap objects are named `orphan.scan.<job>.rados.<shard>`, `.buckets.<shard>`, and `.linked.<shard>`. `search_stage.shard` and `search_stage.marker` are saved while iterating bucket index shards, allowing partial resume. `finish()` removes temporary objects and job state. `RGWRadosList` does not persist state; it holds in-memory `bucket_process_map` and `visited_oids`.

## Dependencies and integration points
The code integrates with RGW SAL/RadosStore, RGWRados bucket/object APIs, metadata listing, bucket instance parsing/loading, bucket reshard state, object manifests, multipart upload abstractions, DLO/SLO attrs, Ceph bufferlist encoding, log pool ioctx, and Ceph admin formatter/dout output. It is intended for `radosgw-admin` commands and operational diagnostics.

## Risks and edge cases
- The search is inherently racy with object create/delete, bucket delete, and reshard; the code skips some races but can still produce false positives/negatives.
- `obj_fingerprint()` loops backward with unsigned `size_t`; unusual short object names or suffixes deserve tests.
- `RGWOrphanStore::store_entries()` and `read_entries()` currently return 0 even after logging certain lower-level errors, which can hide persistence failures.
- `log_oids()` batches 100 entries per omap write and the scan can create many omap keys; large clusters need operational limits.
- The comparison assumes shard omap key ordering by fingerprint-compatible strings and uses empty `cur_linked` initial state carefully; edge ordering bugs would affect leak results.
- Indexless buckets make `radoslist` incomplete unless explicitly bypassed.
- DLO/SLO recursion is bounded only by `visited_oids` for object IDs and the evolving bucket process map.

## Test signals
Tests should simulate job create/resume/finish, omap read/write/list/remove errors, bucket-instance sharding, pool objects with heads/shadows/multipart suffixes, stale threshold boundaries, bucket deletion races, reshard skip behavior, manifest traversal for multipart/versioned/head-only objects, DLO/SLO references including loops and malformed paths, indexless bucket behavior, field-separator output, and incomplete multipart listing. Integration tests need a controlled RGW/RADOS fixture because most behavior depends on live metadata and object manifests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/radosgw-admin/orphan.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/radosgw-admin/orphan.h -->
# sources/distributed-fs/ceph/src/rgw/radosgw-admin/orphan.h

## Purpose
This header declares the state model and public classes for RGW orphan search and RADOS object listing used by `radosgw-admin` tooling.

## Important APIs, types, and functions
- Constants: `RGW_ORPHAN_INDEX_OID` (`orphan.index`) and `RGW_ORPHAN_INDEX_PREFIX` (`orphan.scan`).
- `RGWOrphanSearchStageId` enumerates persisted stages from init through pool listing, bucket listing, bucket-index iteration, and comparison.
- `RGWOrphanSearchStage`, `RGWOrphanSearchInfo`, and `RGWOrphanSearchState` encode/decode and dump job metadata and progress.
- `RGWOrphanStore` wraps log-pool omap access for jobs and shard entries.
- `RGWOrphanSearch` declares the staged orphan scan, shard index maps, concurrency/staleness configuration, state saving, index builders, compare, run, and finish.
- `RGWRadosList` declares traversal helpers for listing raw RADOS objects behind RGW buckets and manifests.

## Control flow
The header defines the stage machine consumed by `orphan.cc`: `INIT -> LSPOOL -> LSBUCKETS -> ITERATE_BI -> COMPARE`. It also defines private helpers for sharding fingerprints, logging object IDs, handling async stat results, and removing temporary index objects.

## State and persistence behavior
The encoded structs are the durable job contract. `RGWOrphanSearchInfo` version 2 stores job name, target pool, shard count, and start time; `RGWOrphanSearchStage` stores stage, current shard, and marker; `RGWOrphanSearchState` combines both. `RGWOrphanSearch` keeps in-memory maps from shard id to temporary omap object names. `RGWRadosList` keeps in-memory bucket processing and visited-object state only.

## Dependencies and integration points
The header depends on Ceph config, formatter, errno helpers, and `rgw_sal_rados.h`. It exposes RGW SAL RadosStore types, librados IoCtx, `DoutPrefixProvider`, `bufferlist`, `rgw_pool`, and RGW object key types to the implementation and callers.

## Risks and edge cases
- Encoding versions must remain compatible with existing persisted orphan jobs.
- `num_shards` is a `uint16_t`; the implementation hashes into this count and assumes it is nonzero after defaulting.
- Public constructors take raw `RadosStore*`; lifetime is owned elsewhere.
- Operational safety depends on callers invoking `finish()` after successful searches to remove temporary omap objects.

## Test signals
Tests should round-trip encode/decode for all persisted structs, verify formatter output for each stage, validate default and explicit shard counts, confirm temporary object naming from job/shard data, and exercise class APIs through the implementation with mocked or fixture-backed RadosStore behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/radosgw-admin/orphan.h -->
