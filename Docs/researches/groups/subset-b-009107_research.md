# subset-b-009107 research

Grouped research report for Borg testsuite compression, crypto, helper, legacy, pattern, locking, item, logger, and platform test files. Each source file section is delimited for deterministic source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/compress_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/compress_test.py

Purpose: exercises Borg's compression facade and `CompressionSpec` parser across `none`, `lz4`, `zlib`, legacy zlib, `lzma`, `zstd`, `auto`, and size-obfuscating wrappers.

Important APIs and control flow: tests call `get_compressor`, `Compressor.compress`, `Compressor.decompress`, and `CompressionSpec(...).compressor`. Parametrized cases verify compressor class lookup, metadata fields (`ctype`, `clevel`, `csize`, `size`, `psize`), autodetection through the generic `Compressor`, legacy zlib wire compatibility, invalid compressed data handling, default and explicit level parsing, and `ArgumentTypeError` on malformed specs. Obfuscation tests cover reciprocal factor specs, additive padding specs, padme sizing (`obfuscate,250`), and object-type filtering via `ROBJ_FILE_STREAM` versus `ROBJ_ARCHIVE_META`.

State and persistence: no persistent repository state is written. Tests allocate temporary in-memory data and one 50 MiB incompressible blob to stress LZ4 buffer sizing. Randomized obfuscation assertions depend on repeated compression producing multiple output lengths.

Dependencies and integration points: depends on `borg.compress`, `borg.helpers.CompressionSpec`, Borg object-type constants, Python `zlib`, and pytest parametrization/monkeypatching. It is a contract test for archive chunk metadata consumed by repository object storage and legacy upgrade code.

Risks: output-size tests use broad statistical/range assertions and can become flaky if padding algorithms or compression ratios change. The large LZ4 test has memory cost. Legacy zlib compatibility is intentionally strict because Borg 1.x data lacks the newer extra header.

Test signals: successful round trips, exact zlib byte equality, expected metadata, parser errors, and object-type-specific no-padding for archive metadata signal compression compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/compress_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/crypto/__init__.py -->
# sources/sync-backup/borg/src/borg/testsuite/crypto/__init__.py

Purpose: package marker for crypto tests under `borg.testsuite.crypto`.

Important APIs and control flow: the file defines no imports, helpers, fixtures, or runtime logic. Its function is to make sibling modules importable as a package.

State and persistence: no state is read or written.

Dependencies and integration points: integration is Python package discovery for tests that use relative imports from `...crypto` and `..`.

Risks: the risk is structural rather than behavioral; removing it can change package import semantics in older tooling or direct test invocation modes.

Test signals: import collection of the crypto test package is the only signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/crypto/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/crypto/crypto_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/crypto/crypto_test.py

Purpose: self-test-compatible crypto test module covering low-level cipher envelopes, fixed vectors, key-file decryption, repository key detection regressions, and `KeyBase.derive_key`.

Important APIs and control flow: `CryptoTestCase` uses `BaseTestCase` without pytest imports because Borg selftest imports it directly. It tests `bytes_to_int`, `bytes_to_long`, `long_to_bytes`, `UNENCRYPTED`, `AES256_CTR_HMAC_SHA256`, `AES256_OCB`, and `CHACHA20_POLY1305`. The cipher tests build headers/AAD, encrypt fixed plaintext, slice envelope fields, compare hex MAC/IV/ciphertext vectors, validate `next_iv`, then corrupt data or AAD and require `IntegrityError`. Standalone tests construct msgpack key-file envelopes for Argon2 plus ChaCha20-Poly1305 and PBKDF2 plus AES-CTR/HMAC, then call `decrypt_key_file`. A regression test ensures `AESOCBKey.detect` treats wrong passphrase decryption as candidate failure instead of leaking low-level integrity errors. `TestDeriveKey` defines a minimal `KeyBase` subclass and verifies salt/domain/key-material separation, including `from_id_key=True`.

State and persistence: mostly in-memory. The key-detection regression uses a mocked repository with stored key bytes and environment `BORG_DISPLAY_PASSPHRASE=no`; no disk state is required.

Dependencies and integration points: depends on Cython low-level crypto classes, legacy AES/PBKDF2 code, msgpack helpers, key classes (`CHPOKey`, `AESOCBKey`, `PlaintextKey`, `KeyBase`), `getpass`, `unittest.mock`, and selftest's `BaseTestCase`. It integrates with Borg's selftest count and therefore has stricter import constraints.

Risks: fixed crypto vectors are intentionally brittle and will fail on envelope layout changes, MAC/AAD offset changes, or IV accounting changes. The selftest warning means adding/removing test methods must keep Borg's selftest metadata in sync.

Test signals: exact vector matches, corruption-triggered `IntegrityError`, successful key-file decrypt, non-raising repo-key detection, and expected derived key bytes are the primary signals.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/crypto/crypto_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/crypto/csprng_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/crypto/csprng_test.py

Purpose: validates deterministic and range-correct behavior of Borg's keyed `CSPRNG` helper.

Important APIs and control flow: tests instantiate `CSPRNG` with two fixed 32-byte keys. They compare deterministic `random_bytes` output for same-key instances, verify different keys differ, exercise byte lengths from 1 through 10000, call `random_int` over small, large, power-of-two, and adjacent bounds, and require `ValueError` for non-positive bounds. Shuffle tests verify deterministic same-key permutations, different-key differences, continued-stream differences, and large-list permutation preservation.

State and persistence: no persistent state. The generator has internal stream/counter state visible through the "same RNG used again gives a different shuffle" assertion.

Dependencies and integration points: depends on `borg.crypto.low_level.CSPRNG` and pytest. The generator is relevant to chunk-size obfuscation and any deterministic keyed randomization inside Borg.

Risks: statistical tests over 10000 bytes use fixed but probabilistic uniformity thresholds. A correct CSPRNG with a changed algorithm could still break deterministic-vector expectations indirectly through distribution thresholds or shuffle order.

Test signals: deterministic equality for same key, inequality for different keys, valid bounds, permutation preservation, byte-count distribution, and bit-count distribution.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/crypto/csprng_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/crypto/file_integrity_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/crypto/file_integrity_test.py

Purpose: tests Borg's file integrity wrappers for detached `.integrity` files, inline integrity data, part-level hashing, `SyncFile` integration, and SHA-256 hashing behavior.

Important APIs and control flow: `TestReadIntegrityFile` covers missing, truncated, unknown-algorithm, and malformed integrity metadata. `TestDetachedIntegrityCheckedFile` writes protected data, verifies normal reads, detects appended corruption, detects corruption even after partial reads, treats rename as path-bound integrity failure, permits moving a file and sidecar together, and tolerates missing integrity files. `TestDetachedIntegrityCheckedFileParts` validates named part hashes, wrong part names, and independence of verified leading parts from later appended corruption while still failing final digest. `TestIntegrityCheckedFileWithSyncFile` wraps a `SyncFile` override and reuses captured `integrity_data`. `TestSHA256FileHashingWrapper` checks pure and impure hash modes, including file-length suffixing in impure mode.

State and persistence: uses pytest temporary directories to create real files and sidecar `.integrity` JSON files. Integrity depends on file contents, file name/path binding, named parts, and final digest state.

Dependencies and integration points: depends on `DetachedIntegrityCheckedFile`, `IntegrityCheckedFile`, `SHA256FileHashingWrapper`, `FileIntegrityError`, and platform `SyncFile`. This protects repository index/hints/integrity sidecars and other metadata files.

Risks: the API deliberately fails closed after a part hash mismatch, so broad exception handling around `hash_part` still leads to final failure. Rename sensitivity is useful for tamper detection but can surprise callers that rename protected files without regenerating metadata.

Test signals: successful readback, expected `FileIntegrityError` on malformed or corrupted data, path/move behavior, part isolation, and known SHA-256 digests.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/crypto/file_integrity_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/crypto/key_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/crypto/key_test.py

Purpose: broad key-class contract tests covering plaintext, authenticated, legacy AES-CTR, BLAKE2/BLAKE3 authenticated variants, AEAD variants, keyfile/repokey storage, manifest/archive metadata authentication, and unsupported key-file formats.

Important APIs and control flow: `TestKey` defines mock args and a mock repository with `save_key`/`load_key`. Fixtures create keys across plaintext, authenticated, AES-CTR, BLAKE2, AES-OCB, ChaCha20-Poly1305, and BLAKE3 variants using `BORG_PASSPHRASE`. Tests validate plaintext hash/decrypt, keyfile creation and IV progression, `BORG_KEY_FILE` override, Borg 2 keyfile fixtures, BLAKE2 id hash fixture, legacy named keyfile fallback, byte-by-byte encrypted-data corruption, `identify_key`/`detect`/decrypt round trips, `assert_id`, authenticated envelope type bytes, and BLAKE2/BLAKE3 id-key sizes. `TestTAM` verifies future msgpack marker handling and legacy metadata pack/unpack without `tam`. Standalone tests cover unsupported algorithms, unsupported version 2, Argon2 key-file roundtrip through repository storage, and wrong passphrase returning `None`.

State and persistence: writes temporary key files under `BORG_KEYS_DIR` or `BORG_KEY_FILE`, stores repokey bytes in mocked repository methods, and mutates environment variables for passphrase and key location behavior.

Dependencies and integration points: depends on key classes and constants from `borg.crypto.key`, low-level `IntegrityError`, helpers `Location`, msgpack, hex/base64 conversion, and `KEY_ALGORITHMS`. It integrates with repository key storage, manifest TAM behavior, chunk id hashing, and legacy key formats.

Risks: fixture key strings and encrypted chunks are exact compatibility fixtures. Changes to key-file formatting, default storage, IV block accounting, or key type bytes must update tests deliberately. Some APIs intentionally return `None` for wrong passphrase while raising for unsupported formats, so error semantics are part of the contract.

Test signals: decryptable fixtures, expected environment-based key path behavior, corruption failures, type-byte/id-hash matches, metadata round trips, and helpful unsupported-format exceptions.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/crypto/key_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/crypto/legacy_key_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/crypto/legacy_key_test.py

Purpose: focused regression tests for Borg 1.x `Pbkdf2FileMixin` key-file encryption/decryption behavior.

Important APIs and control flow: tests instantiate legacy `AESCTRKey`, encrypt plaintext key material with passphrase and `"sha256"` algorithm, decrypt it back, confirm wrong passphrases return `None`, and pass a msgpack blob with unsupported `version=99` to require `UnsupportedKeyFormatError`.

State and persistence: all data is in-memory msgpack blobs. No key files are written.

Dependencies and integration points: depends on `borg.legacy.crypto.key.AESCTRKey`, `borg.helpers.msgpack`, and modern `UnsupportedKeyFormatError`. It supports legacy repository/key migration and compatibility handling.

Risks: wrong passphrase returning `None` is an interface contract used by key detection. Unsupported-version handling must remain an explicit error rather than silent failure.

Test signals: PBKDF2 roundtrip success, wrong-passphrase `None`, and unsupported-version exception.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/crypto/legacy_key_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/fslocking_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/fslocking_test.py

Purpose: validates Borg filesystem lock primitives: timeout timers, exclusive directory locks, shared/exclusive roster locks, stale lock cleanup, lock migration after daemonization, and roster persistence.

Important APIs and control flow: `free_pid` finds a likely unused local PID using `get_process_id` and `process_alive`. `TestTimeoutTimer` verifies timeout and sleep pacing. `TestExclusiveLock` covers context manager acquisition, break/reacquire, timeout when owned, killing stale local locks, refusing unknown remote-host locks, lock ID migration, and a Windows-skipped 40-thread race loop that asserts no concurrent exclusive holders. `TestLock` covers shared coexistence, exclusive acquisition, upgrade/downgrade idempotence, exclusive-state queries, break, timeout matrix, stale cleanup, and migration for both modes. `TestLockRoster` verifies serialized roster load/save, add/remove semantics, stale local lock pruning while keeping unknown remote locks, and roster ID migration.

State and persistence: writes lock files and roster files under pytest temporary directories. State is keyed by `(host, pid, tid)` identity and is intentionally sensitive to whether a PID is live on the local host.

Dependencies and integration points: depends on `borg.fslocking` (`TimeoutTimer`, `ExclusiveLock`, `Lock`, `LockRoster`, constants, exceptions), platform PID helpers, threading, and `is_win32`. Repository and cache code rely on these locks for concurrency safety.

Risks: free-PID selection is inherently racy. The threaded race test is timing-sensitive and skipped on Windows. Remote-host stale locks cannot be proven dead and therefore intentionally block acquisition.

Test signals: expected timeout/exception behavior, roster contents, lock ownership checks, successful migration, and no concurrent exclusive holders in the stress test.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/fslocking_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/hashindex_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/hashindex_test.py

Purpose: tests `ChunkIndex` entry insertion, pack-location updates, missing-key behavior, struct bounds, and tracking of newly added entries.

Important APIs and control flow: helpers `H` and `H2` generate deterministic 32-byte keys. `test_chunkindex_add` adds a chunk with unknown pack location, allows size fill-in from zero, rejects inconsistent size updates, and checks `ChunkIndexEntry` fields. `test_chunkindex_update_pack_info` updates multiple chunks with pack id, offsets, and object sizes, then confirms `None` and empty updates are no-ops. `test_keyerror` checks missing lookup and oversize struct packing. `test_new` exercises `iteritems(only_new=True)` and `clear_new`.

State and persistence: in-memory hash index only. The "new" bitset/state is mutable and explicitly cleared.

Dependencies and integration points: depends on `borg.hashindex.ChunkIndex`, `ChunkIndexEntry`, and sentinel constants `UNKNOWN_INT32`/`UNKNOWN_BYTES32`. It supports cache and repository object-location bookkeeping.

Risks: C-extension struct limits can surface as `struct.error`; field widths and flag names are part of the compatibility contract.

Test signals: exact entry equality, no-op update behavior, expected exceptions, and new-entry iterator state.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/hashindex_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/__init__.py -->
# sources/sync-backup/borg/src/borg/testsuite/helpers/__init__.py

Purpose: package marker for helper tests under `borg.testsuite.helpers`.

Important APIs and control flow: the file has no code. It exists for package collection and relative imports in sibling test modules.

State and persistence: no state.

Dependencies and integration points: Python test discovery and relative import semantics.

Risks: removing it can affect direct module execution or older pytest import modes.

Test signals: successful collection of helper tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/__init__test.py -->
# sources/sync-backup/borg/src/borg/testsuite/helpers/__init__test.py

Purpose: validates helper-level exit-code classification and aggregation.

Important APIs and control flow: parametrized `test_classify_ec` checks inclusive/exclusive ranges for success, warning, error, and signal classes across legacy and modern Borg exit-code bases. `test_ec_invalid` checks out-of-range and type errors. `test_max_ec` verifies severity ordering, with modern warning/error subcodes choosing the lower code within a class but more severe classes winning overall.

State and persistence: no persistent state.

Dependencies and integration points: depends on constants such as `EXIT_SUCCESS`, `EXIT_WARNING_BASE`, `EXIT_ERROR_BASE`, `EXIT_SIGNAL_BASE`, and helpers `classify_ec` and `max_ec`. It integrates with command exit handling and multi-error aggregation.

Risks: one assertion in `test_classify_ec` calls `classify_ec(ec) == ec_class` without `assert`, so this test currently only checks that valid ranges do not raise. `max_ec` carries most behavioral verification.

Test signals: invalid input exceptions and exact maximum-exit-code outcomes.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/__init__test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/datastruct_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/helpers/datastruct_test.py

Purpose: tests deterministic dictionary ordering and reusable buffer sizing.

Important APIs and control flow: `test_stable_dict` verifies `StableDict` sorts items by key and produces a stable msgpack MD5 digest. `TestBuffer` checks backing type creation, initial lengths, grow/shrink behavior, `init=True` forcing reallocation, memory limit enforcement, and `get(size)` reusing or resizing as needed.

State and persistence: in-memory structures only. `Buffer` preserves and reuses internal allocated capacity until explicit reinitialization or growth.

Dependencies and integration points: depends on `StableDict`, `Buffer`, `helpers.msgpack`, and hashlib. Stable serialization affects archive metadata and cache hashes; `Buffer` supports performance-sensitive binary processing.

Risks: stable digest fixtures can break on msgpack configuration changes. `Buffer` allows retained larger allocations after shrink requests, which is intentional but relevant for memory-sensitive callers.

Test signals: exact item ordering, known MD5, allocation identity checks, and `MemoryLimitExceeded`.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/datastruct_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/efficient_collection_queue_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/helpers/efficient_collection_queue_test.py

Purpose: verifies `EfficientCollectionQueue` behavior for byte and list collections with bounded front chunks.

Important APIs and control flow: tests create queues with chunk size and collection factory, inspect empty `peek_front`, push data, check total length and truthiness, pop exact sizes, verify chunk-boundary behavior, and require `SizeUnderflow` when popping more than available.

State and persistence: in-memory queue state tracks appended chunks, total length, and front consumption.

Dependencies and integration points: depends on `helpers.datastruct.EfficientCollectionQueue`. It supports stream assembly/consumption code that needs efficient front slicing without repeatedly copying whole buffers.

Risks: semantics differ by collection type (`bytes` empty value versus `list` empty value). Underflow must leave remaining data intact.

Test signals: expected front slices, length/truthiness transitions, and underflow exception while preserving queued tail.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/efficient_collection_queue_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/fs_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/helpers/fs_test.py

Purpose: tests filesystem helper path resolution, safe deletion, path sanitization, cache/tag detection, dash stdio handling, and Windows character mapping.

Important APIs and control flow: environment tests cover `get_base_dir`, `get_config_dir`, `get_cache_dir`, `get_keys_dir`, `get_security_dir`, and `get_runtime_dir` across Windows, Darwin, and other POSIX branches, including `BORG_*` overrides and XDG variables. `dash_open` maps `-` to stdio streams. Hardlink-skipped tests ensure `safe_unlink` does not destroy a hardlinked victim and still preserves it on simulated `ENOSPC`. Path tests exercise `remove_dotdot_prefixes`, `make_path_safe`, rejected dot-dot paths, and Windows drive-letter normalization. `test_dir_is_tagged` creates real directories with valid/invalid `CACHEDIR.TAG` and custom tag files, then tests both path and directory-fd lookup modes. `test_map_chars` verifies Windows private-use substitutions for reserved filename characters.

State and persistence: writes temporary directories, files, hardlinks, tag files, and environment variables. Directory tag detection reads both path-based and fd-relative state.

Dependencies and integration points: depends on `helpers.fs`, Borg cache-tag constants, platform flags, and testsuite helpers for hardlink support and rejected dot-dot paths. These helpers are used by repository/key/cache path discovery and archive extraction safety.

Risks: platform-specific defaults are branchy and can be fragile under MSYS/Cygwin, Haiku, CI runtime-dir layouts, or unusual HOME/USER settings. Path safety must reject traversal without over-normalizing legitimate names.

Test signals: exact path outputs under controlled env vars, hardlink victim preservation, expected `ValueError`, tag lists for every directory case, and Windows character mapping.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/fs_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/lrucache_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/helpers/lrucache_test.py

Purpose: tests Borg's small `LRUCache` mapping and disposal hook.

Important APIs and control flow: `test_lrucache` inserts three keys into a capacity-2 cache, checks eviction, membership, `items`, indexing, `get` with default, deletion, and clearing. `test_dispose` stores temporary files with a dispose callback and asserts evicted, deleted, and cleared values are closed while retained values are not.

State and persistence: in-memory cache state plus temporary file handles that reveal disposal state.

Dependencies and integration points: depends on `helpers.lrucache.LRUCache` and `TemporaryFile`. LRU behavior is used for file descriptor/object caching.

Risks: disposal side effects must run exactly once for removed values and not for retained values. Access order versus insertion order is part of cache semantics.

Test signals: expected retained key set, `KeyError`, default lookup, and file `.closed` transitions.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/lrucache_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/misc_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/helpers/misc_test.py

Purpose: tests miscellaneous iterator/file-wrapper helpers.

Important APIs and control flow: `ChunkIteratorFileWrapper` is read with small and large sizes over byte chunks and must report exhaustion. `chunkit` chunks iterables into fixed-size lists and remains exhausted on repeated `next`. `iter_separated` reads separated text and byte streams using newline, NUL, and multi-character separators, including trailing separators.

State and persistence: in-memory `StringIO`/`BytesIO` and iterator state only.

Dependencies and integration points: depends on `helpers.misc.ChunkIteratorFileWrapper`, `chunkit`, and `iter_separated`. These are integration helpers for command inputs, chunk streams, and separated lists.

Risks: EOF/exhaustion behavior is easy to get wrong, especially with trailing separators and bytes-versus-text streams.

Test signals: exact read fragments, chunk lists, and separated item lists.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/misc_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/msgpack_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/helpers/msgpack_test.py

Purpose: verifies detection of slow pure-Python msgpack fallback while skipping environments where slow msgpack is expected.

Important APIs and control flow: `expected_py_mp_slow_combination` imports upstream `msgpack`, returns true for Cygwin and Python 3.12 with msgpack older than 1.0.6, and is used as a skip condition. The test temporarily replaces `msgpack.Packer` with `msgpack.fallback.Packer` to require `is_slow_msgpack()`, then restores it and requires fast detection.

State and persistence: mutates the imported `msgpack.Packer` symbol in-process and restores it in `finally`.

Dependencies and integration points: depends on upstream msgpack internals, Borg `helpers.msgpack.is_slow_msgpack`, Python version, and Cygwin platform flag. Borg warns or adapts based on msgpack performance.

Risks: relies on upstream `msgpack.fallback.Packer` existing and on wheel availability assumptions. Failing to restore `msgpack.Packer` would leak process-global state, but the test uses `finally`.

Test signals: slow detection under forced fallback and fast detection under the real packer.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/msgpack_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/nanorst_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/helpers/nanorst_test.py

Purpose: tests Borg's minimal reStructuredText-to-text converter.

Important APIs and control flow: cases cover inline emphasis/literal markup stripping, multi-line inline spans, inline escaped asterisks, comments with and without blank-line directive context, `.. note::` directive rendering, reference substitution with a provided map, undefined-reference errors, and code-block text at end of string.

State and persistence: pure string transformation; no persistent state.

Dependencies and integration points: depends on `helpers.nanorst.rst_to_text`. It supports help/doc text rendering in contexts where full docutils is unnecessary.

Risks: parser intentionally handles a tiny rst subset. Ambiguous comment/directive layout and undefined references are the main behavioral edges.

Test signals: exact rendered strings and `ValueError` for missing references.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/nanorst_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/parseformat_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/helpers/parseformat_test.py

Purpose: comprehensive tests for parse/format helpers: binary/text JSON encoding, repository locations, archive/text validators, time intervals, timestamps, file sizes, placeholder formatting, display-width slicing, escape evaluation, and chunker parameter parsing.

Important APIs and control flow: early tests cover `bin_to_hex`, `binary_to_json`, and `text_to_json` including surrogateescape fallback with `_b64` fields. `TestLocationWithoutEnv` removes `BORG_REPO` and verifies `Location` parsing/canonicalization for ssh/rest IPv4/IPv6 forms, file paths, s3/b2/rclone/sftp/http passthrough with credential stripping, local absolute/relative paths, SMB-style paths, colons, canonical idempotence, and bad syntax. Validators reject invalid archive names, control characters, NULs, surrogate escapes, and length violations. Formatting tests cover `format_timedelta`, `interval`, `parse_timestamp`, SI/IEC file-size formatting, parsing file-size suffixes, `partial_format`, `clean_lines`, `format_line`, placeholder errors, `replace_placeholders`, `swidth_slice`, `eval_escapes`, and `ChunkerParams` for buzhash/fixed modes and invalid boundaries.

State and persistence: mostly pure parsing. It mutates environment variables, uses current time for `{now}`, and conditionally skips display-width tests depending on platform `swidth`.

Dependencies and integration points: depends on constants, `helpers.argparsing.ArgumentTypeError`, `helpers.parseformat`, `helpers.time`, and platform flags. These helpers integrate with CLI argument parsing, repository location identity/security, archive naming, output formatting, and chunker configuration.

Risks: location parsing is security-sensitive because credentials must be stripped from canonical paths while raw processed URLs remain usable. Placeholder formatting guards against attribute traversal. Chunker parameter validation must prevent unsupported memory/object sizes.

Test signals: exact `repr(Location)`, canonical path idempotence, expected exceptions, file-size strings, placeholder outputs, escape results, and chunker tuple values.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/parseformat_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/passphrase_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/helpers/passphrase_test.py

Purpose: tests passphrase prompting, display/debug controls, retry behavior, empty-passphrase rejection, and secret-safe representations.

Important APIs and control flow: `Passphrase.new` is tested with monkeypatched `getpass.getpass`, `BORG_DISPLAY_PASSPHRASE` on/off, non-ASCII passphrases, printable special characters, empty input, and repeated mismatches causing `PasswordRetriesExceeded`. `repr(Passphrase)` must not reveal the secret. `display_debug_info` only prints wrong passphrase and related environment variables when `BORG_DEBUG_PASSPHRASE=YES`. `verification` prints plaintext and hex only when display is enabled.

State and persistence: mutates environment variables and captures stderr/stdout with pytest. No secrets are written to disk.

Dependencies and integration points: depends on `helpers.passphrase.Passphrase`, `PasswordRetriesExceeded`, `getpass`, and hex conversion. It integrates with key creation/detection and CLI safety.

Risks: tests deliberately check for absence of secrets in normal output. Debug modes intentionally leak passphrases when enabled, so gating must remain strict.

Test signals: captured output contains or omits passphrase/hex text as expected, retries fail with the right exception, and `repr` redacts.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/passphrase_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/process_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/helpers/process_test.py

Purpose: tests subprocess command parsing and error handling wrapper behavior.

Important APIs and control flow: `TestPopenWithErrorHandling` runs `test 1` when available, expects `None` for a definitely missing command, expects `None` for bad shell-like command syntax and empty strings, and asserts `shell=True` is rejected.

State and persistence: launches a short process only for the simple case. No persistent state.

Dependencies and integration points: depends on `shutil.which`, pytest skips/parametrization, and `helpers.process.popen_with_error_handling`. It protects helpers that run external commands such as passphrase commands or remote transports.

Risks: availability of the POSIX `test` command is platform-dependent. The missing-command name must remain absent from PATH for the skip logic to be meaningful.

Test signals: process exit code zero, `None` on parse/not-found failure, and assertion on forbidden shell mode.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/process_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/progress_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/helpers/progress_test.py

Purpose: tests percentage progress indicator output cadence and quiet mode.

Important APIs and control flow: tests instantiate `ProgressIndicatorPercent` with totals, steps, starts, and message format, set logger level, call `show` with explicit or implicit current values, and call `finish`. They assert initial, stepped, final, and trailing newline stderr output. Quiet mode sets logger level to WARN and expects no output.

State and persistence: in-memory indicator state tracks current progress and last emitted percentage. Captured stderr is the observable state.

Dependencies and integration points: depends on `helpers.progress.ProgressIndicatorPercent` and pytest `capfd`. It integrates with CLI progress reporting.

Risks: output formatting is exact, including spaces and final newline. Logger level controls visibility.

Test signals: exact captured stderr strings and silence in quiet mode.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/progress_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/shellpattern_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/helpers/shellpattern_test.py

Purpose: verifies Borg's shell-pattern-to-regex translator for literals, separators, glob stars, double-stars, character sets, inverted sets, groups, Unicode, and custom match endings.

Important APIs and control flow: helper `check` compiles `shellpattern.translate(pattern)` and matches paths. Large parametrized match/mismatch tables cover `?`, `*`, `**` across path separators, nested directory matching, sets including `]`, inverted sets, brace groups including nested groups and empty alternatives, non-ASCII characters, and escaping-like literal behavior. `test_match_end` verifies default end-of-string matching and a custom optional suffix regex.

State and persistence: pure regex compilation/matching; no persistent state.

Dependencies and integration points: depends on `helpers.shellpattern.translate`, Python `re`, and pytest. This translator backs include/exclude pattern semantics.

Risks: separator handling is subtle: single-star and question mark must not cross separators, while `**/` has directory-layer semantics. Brace parsing can be ambiguous with malformed groups.

Test signals: every pattern in match tables must match and every mismatch case must not, plus exact custom suffix behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/shellpattern_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/time_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/helpers/time_test.py

Purpose: tests timestamp clamping helpers for nanoseconds and seconds on 32-bit and wider platforms.

Important APIs and control flow: `utcfromtimestamp` wraps `datetime.fromtimestamp(..., timezone.utc)` and strips tzinfo. `test_safe_timestamps` branches on `SUPPORT_32BIT_PLATFORMS`; both branches clamp negative values to zero, clamp huge nanoseconds into signed int64, and ensure huge seconds do not overflow datetime. The 32-bit branch clamps seconds to int32, while the wider branch clamps seconds so nanosecond conversion still fits int64.

State and persistence: pure numeric/date operations.

Dependencies and integration points: depends on `helpers.time.safe_ns`, `safe_s`, and `SUPPORT_32BIT_PLATFORMS`. These functions protect archive item timestamps and platform conversion code.

Risks: platform datetime ranges vary, and the tests intentionally use extremely large values that would otherwise hit Python's Y10K/overflow limits.

Test signals: no overflow after clamping, negative-to-zero behavior, and post-2038/post-2262 sanity thresholds.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/time_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/yes_no_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/helpers/yes_no_test.py

Purpose: tests interactive yes/no prompting, environment overrides, defaults, retry behavior, custom truthy/falsy sets, and user-facing output.

Important APIs and control flow: tests feed `FakeInputs` containing `TRUISH`, `FALSISH`, `DEFAULTISH`, invalid inputs, and custom values into `yes`. Environment override tests set a variable and bypass input. Defaults are checked for blank/defaultish/no-input cases, with `default=None` raising `ValueError`. Retry and no-retry paths verify how invalid inputs are handled. Output tests assert stderr contains intro, retry, true/false, and environment override messages while stdout remains empty.

State and persistence: mutates environment variables and consumes `FakeInputs`; no disk state.

Dependencies and integration points: depends on `helpers.yes_no.yes`, constants `TRUISH`, `FALSISH`, `DEFAULTISH`, and testsuite `FakeInputs`. It supports CLI confirmations and noninteractive env overrides.

Risks: default handling can silently choose actions when input is exhausted. Environment override values are printed, so output should avoid leaking unrelated secrets.

Test signals: boolean decisions, expected exceptions, and exact stderr inclusion/exclusion.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/helpers/yes_no_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/item_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/item_test.py

Purpose: tests Borg `Item` typed property behavior, serialization dictionary shape, file-size derivation, opaque pointer roundtrip, and chunk-content comparison.

Important APIs and control flow: tests cover empty item membership/get/attribute errors, construction from bytes or string keys, invalid inputs, keyword construction, int property type checks, msgpack timestamp conversion for `atime`, surrogateescaped string properties for non-UTF-8 paths, list and `StableDict` properties, rejection of unknown attributes, `get_size` with and without `memorize`, `to_optr`/`from_optr`, and `chunks_contents_equal` across equal chunk boundaries, exhaustion, mismatch, and prefix cases.

State and persistence: in-memory `Item` internal dict state and typed property descriptors. `memorize=True` persists computed `size` inside the item.

Dependencies and integration points: depends on `borg.item.Item`, `chunks_contents_equal`, `ChunkListEntry`, `StableDict`, and msgpack `Timestamp`. `Item` is central to archive metadata, extraction, and legacy upgrade.

Risks: unknown-key rejection protects metadata schema. Surrogateescape path handling is important for round-tripping non-UTF-8 filesystem names.

Test signals: exact `as_dict` output, typed exceptions, timestamp wrapper conversion, size calculation, optr identity, and symmetric chunk comparison results.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/item_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/legacy_archives_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/legacy_archives_test.py

Purpose: tests `LegacyArchives`, Borg 1.x manifest archive listing compatibility, archive metadata loading, filtering, and manifest dispatch for legacy repositories.

Important APIs and control flow: helper factories build mock archive dictionaries, `ArchiveInfo` objects, and controlled list targets. Tests cover initialization, raw dict get/set, prepare/finish, IDs/count/names, existence, creation with string or datetime timestamps, overwrite, lookup by name/id, raw output, and unsupported id-based mutation methods raising `NotImplementedError`. `_get_archive_meta` is tested for repository object missing, successful parse/unpack through `ArchiveItem`, and bad metadata version. Listing tests cover sorting, reverse, first/last slicing, date filtering delegation, match filters for name/user/host/tags/archive-id prefix, ambiguous IDs, `get_one`, and `list_considering` argument validation/delegation. Final tests assert `LegacyArchives` satisfies `ArchivesInterface` and that `Manifest` creates it for a legacy repository subclass.

State and persistence: mostly mocked in-memory repository/manifest state. Archive dictionaries store ids and ISO timestamps. Metadata loading simulates repository object reads through mocks.

Dependencies and integration points: depends on `LegacyArchives`, `LegacyRepository`, `Manifest`, `ArchiveInfo`, `ArchivesInterface`, `PlaintextKey`, CLI `Namespace`, and error classes. It is the compatibility layer between Borg 1.x manifests and Borg 2 archive interfaces.

Risks: many methods are intentionally not implemented for legacy archives; callers must not assume full modern archive mutation support. Archive ID prefix matching can be ambiguous and must error.

Test signals: exact dict/list outputs, `ArchiveInfo` instances, delegated filters, command errors on 0/multiple matches, and manifest dispatch to legacy archive interface.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/legacy_archives_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/legacy_helpers_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/legacy_helpers_test.py

Purpose: tests helper predicates used to interpret Borg 1.x hardlink metadata during migration.

Important APIs and control flow: helper `_item` builds an `Item` with mode/path/mtime and optional legacy fields. Tests verify `borg1_hardlinkable` returns true for regular files, block devices, character devices, and FIFOs, and false for symlinks, directories, and sockets. `borg1_hardlink_master` requires a truthy `hardlink_master` flag. `borg1_hardlink_slave` requires a `source` and a hardlinkable mode, including non-regular hardlinkable types.

State and persistence: in-memory `Item` metadata only.

Dependencies and integration points: depends on `stat`, `Item`, and `borg.legacy.helpers`. These predicates feed `UpgraderFrom12To20` hardlink handling.

Risks: hardlinkability differs from normal-file-only assumptions; FIFOs and device nodes are included for Borg 1 compatibility. Symlink source means target in modern metadata, so mode matters.

Test signals: boolean predicate results for each file type and legacy field combination.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/legacy_helpers_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/legacy_upgrade_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/legacy_upgrade_test.py

Purpose: tests `UpgraderFrom12To20`, converting Borg 1.2 item/archive/chunk metadata into Borg 2-compatible shapes.

Important APIs and control flow: helpers create an upgrader with mock cache/archive and legacy `Item` objects. Item-upgrade tests verify regular pass-through with required keys, whitelist stripping of obsolete fields, removal of `user=None`/`group=None`, symlink `source` to `target`, hardlink master `hlid` creation, hardlink slave `hlid`/chunk reuse from the master, cache `reuse_chunk` calls, and required-key presence. Archive-metadata tests convert `cmdline` and `recreate_cmdline` lists to strings, append UTC offset to naive times, convert 4-tuple chunker params to `(CH_BUZHASH, ...)`, preserve 5-tuples, override when rechunking, drop recreate fields, set empty tags, and omit absent optionals. Compressed-chunk tests promote raw legacy zlib metadata, strip explicit two-byte ctype/clevel prefixes for non-zlib, and upgrade Borg 1 obfuscation headers by extracting big-endian packed compressed size into metadata while preserving padding.

State and persistence: in-memory metadata and mocked cache/archive stats only. The upgrader carries hardlink master mapping during one archive.

Dependencies and integration points: depends on `UpgraderFrom12To20`, `Item`, compression classes/constants, `REQUIRED_ITEM_KEYS`, `CH_BUZHASH`, `ObfuscateSize`, zlib, struct packing, and argparse `Namespace`. It integrates with legacy archive import/migration.

Risks: hardlink slave handling depends on seeing masters before slaves. Chunk compression upgrade is byte-layout-sensitive for Borg 1 headers and obfuscation trailers.

Test signals: expected upgraded item dict keys, cache reuse call, archive metadata fields, promoted compression metadata, and preserved/stripped payload bytes.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/legacy_upgrade_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/legacyrepository_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/legacyrepository_test.py

Purpose: extensive integration tests for Borg 1.x `LegacyRepository` and `LegacyRemoteRepository`, including transactions, segment replay, compaction, shadow indexes, hints/integrity files, repair, and remote RPC command construction.

Important APIs and control flow: fixtures create local and remote legacy repositories, and `pytest_generate_tests` runs selected tests over both. Helpers reopen repositories, convert legacy chunks (`fchunk`, `pchunk`, `pdchunk`), add sample keys, dump segments, manipulate indices/segments, corrupt objects, and list objects. Basic tests cover put/get/delete, commit, rollback, list pagination, max data size, overwrite consistency, and read-data flags. Crash/replay tests remove indices, monkeypatch commit stages, require lock upgrades, ignore commit-tag bytes in data, and clean uncommitted garbage. Compaction tests inspect sparse accounting, delete moved segments, preserve shadowed deletes across index rebuilds, and rollback shadow-index state. Hints/integrity tests corrupt, delete, or make unreadable hints/index files, handle unknown integrity versions, rebuild subtly corrupted hints when integrity detects damage, and log warnings when integrity is missing. Repair tests corrupt or delete data/commit segments and indices, compare non-repair versus repair behavior, ensure no tmp files remain, and validate object sets after repair. Remote tests cover invalid RPC names, transported exception classes/args, SSH command composition with user/port/BORG_RSH/rsh, and borg serve command selection with remote path, log level, and debug topics.

State and persistence: creates real repository directories with `data/0/<segment>`, `index.N`, `hints.N`, `integrity.N`, config, locks, and remote subprocess state. Tests intentionally mutate files to simulate crashes and corruption.

Dependencies and integration points: depends on `LegacyRepository`, `LoggedIO`, `LegacyRemoteRepository`, `NSIndex1`, lock classes, `Location`, msgpack, constants (`MAGIC`, `MAX_DATA_SIZE`, `TAG_*`), compression `CNONE`, and hash helper `H`. It is central compatibility coverage for reading/repairing old repositories.

Risks: many tests depend on exact segment numbering, object header sizes, compact thresholds, and filesystem mutability. Remote tests are skipped on Windows and require the testsuite remote transport. Corruption tests distinguish recoverable damage from data loss, so expected object sets are part of the compatibility contract.

Test signals: repository length/object contents after reopen, `check()` status with and without repair, expected exceptions, compact/shadow index contents, absence of tmp files, logged warnings, and exact remote command/exception behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/legacyrepository_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/logger_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/logger_test.py

Purpose: tests Borg logger setup, parent-module discovery, multiple logger names, and lazy logger proxy methods.

Important APIs and control flow: module-level `logger = create_logger()` is exercised with a `StringIO` handler from `setup_logging`. Tests assert formatted output names for module logger and explicit `logging.getLogger` calls, truncate/reset the stream between cases, check `find_parent_module()`, and call all proxy methods including `exception`.

State and persistence: mutates process logging handlers/levels and captures in-memory stream output.

Dependencies and integration points: depends on `borg.logger.find_parent_module`, `create_logger`, `setup_logging`, Python logging, and pytest fixtures. It affects CLI and internal log routing.

Risks: global logging state can leak between tests if setup does not isolate handlers. Output includes module names and is exact.

Test signals: exact stream contents, correct parent module, and no exceptions from lazy proxy methods.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/logger_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/patterns_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/patterns_test.py

Purpose: comprehensive tests for include/exclude pattern classes, pattern-file parsing, matcher ordering, root validation, Unicode normalization, and regex extraction.

Important APIs and control flow: helper `check_patterns` normalizes inputs and compares matched paths. Parametrized suites cover `PathFullPattern`, `PathPrefixPattern`, `FnmatchPattern`, `ShellPattern`, and `RegexPattern` across absolute/relative paths, duplicate slashes, dot segments, separators, wildcards, `**`, hidden files, and raw regex. Unicode tests compare composed/decomposed/invalid latin1 patterns with Darwin normalization behavior. File-loading tests write temporary exclude and pattern files, call `load_exclude_file`/`load_pattern_file`, and evaluate `PatternMatcher`. They cover comments, whitespace, style switches (`p`/`P`), roots (`R`), illegal commands, include/exclude ordering, `parse_pattern` classes/errors, `IECommand` recursion behavior, root path warning validation, and `get_regex_from_pattern`.

State and persistence: creates temporary pattern files and in-memory matchers. Pattern matcher state is ordered; earlier include/exclude decisions affect later matching.

Dependencies and integration points: depends on `borg.patterns`, `ArgumentTypeError`, Python warnings, filesystem temp paths, and `sys.platform` for Darwin normalization. These semantics drive archive creation/extraction filtering.

Risks: include/exclude order is behaviorally significant. Unicode normalization is platform-dependent. Root path validation warns instead of always failing for missing/relative paths, so callers must handle warnings.

Test signals: exact matched path lists, pattern class instances, warning contents, `ArgumentTypeError`/`ValueError`, matcher fallback behavior, and extracted regex strings.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/patterns_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/platform/__init__.py -->
# sources/sync-backup/borg/src/borg/testsuite/platform/__init__.py

Purpose: package marker for platform-specific tests.

Important APIs and control flow: no code is defined. The file groups `all_test`, OS-specific ACL/sync tests, and shared platform test helpers under one package.

State and persistence: no state.

Dependencies and integration points: Python package import and pytest discovery.

Risks: removing it can affect relative imports such as `.platform_test`.

Test signals: successful collection of platform test modules.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/platform/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/platform/all_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/platform/all_test.py

Purpose: tests platform-neutral functions: string display width and `SyncFile` file-object behavior.

Important APIs and control flow: `swidth` is checked for ASCII, CJK, and mixed strings. `SyncFile` is opened on a temp path in binary mode, writes data, uses `tell`, `seek`, and `read`, then verifies final bytes. Another test closes a `SyncFile` twice to require idempotent close.

State and persistence: writes temporary files and flushes through `SyncFile`.

Dependencies and integration points: depends on `borg.platform.swidth` and `SyncFile`. These support terminal formatting and durable metadata writes across platforms.

Risks: display width depends on platform/wcwidth implementation. `SyncFile` must expose enough file methods for wrapper code and tolerate double close.

Test signals: exact widths, seek/tell positions, persisted bytes, and no exception on repeated close.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/platform/all_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/platform/darwin_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/platform/darwin_test.py

Purpose: Darwin-only tests for extended ACL conversion and durable sync behavior using `F_FULLFSYNC`.

Important APIs and control flow: module-level pytest marks skip non-Darwin and fakeroot environments. ACL helpers call `acl_get`/`acl_set`. `test_extended_acl` writes ACL entries with staff/root UUIDs and checks named and numeric-id forms. `test_fdatasync_uses_f_fullfsync` monkeypatches `fcntl.fcntl` to record calls and requires `F_FULLFSYNC`. `test_fdatasync_falls_back_to_fsync` makes `F_FULLFSYNC` fail and requires one `os.fsync` call. Integration tests call exported `fdatasync` and `sync_dir` on real temporary files/directories.

State and persistence: creates temporary files/directories and mutates ACLs. Monkeypatches process-level `fcntl`/`os.fsync` during tests.

Dependencies and integration points: depends on `borg.platform.acl_get`, `acl_set`, `fdatasync`, `sync_dir`, Darwin platform module, and shared skip markers. These behaviors protect archive ACL preservation and safe file syncing on macOS.

Risks: ACL tests require working ACL support and known group/user mappings. Fullfsync availability and fallback behavior are OS-specific.

Test signals: expected ACL byte substrings, observed `F_FULLFSYNC` call, fallback fsync call, and no exception on integration syncs.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/platform/darwin_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/platform/freebsd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/platform/freebsd_test.py

Purpose: FreeBSD-only ACL tests for access/default ACL round trips and numeric/name conversion.

Important APIs and control flow: module-level marks skip non-FreeBSD and fakeroot. Helpers wrap `acl_get`/`acl_set` with `acl_access`, `acl_default`, and `acl_nfs4` fields. `test_access_acl` checks setting root/wheel named ACL entries, reading named and numeric versions, and preserving explicit numeric ids when requested. `test_default_acl` writes access and default ACL blobs on a directory and expects exact bytes back. NFSv4 ACL testing is noted as not implemented.

State and persistence: creates temporary files/directories and writes ACL metadata.

Dependencies and integration points: depends on Borg platform ACL functions and shared skip markers. Used for archive ACL preservation on FreeBSD.

Risks: requires ACL support and expected root/wheel mappings. Exact ACL byte ordering/format is platform-specific.

Test signals: expected ACL substrings for named/numeric reads and exact access/default ACL roundtrip.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/platform/freebsd_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/platform/linux_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/platform/linux_test.py

Purpose: Linux-only ACL tests for POSIX ACL round trips, non-ASCII names, and numeric/name conversion helpers.

Important APIs and control flow: module-level marks skip non-Linux and fakeroot. Helpers wrap `acl_get`/`acl_set`. Access/default ACL tests set root and numeric entries, then compare named and numeric forms. `test_non_ascii_acl` is additionally skipped unless a user named `ubel` with umlaut exists; it checks non-ASCII user/group ACL roundtrips and numeric conversion. Utility tests import Linux-specific functions for local uid/gid fallback and numeric-to-named/numeric-with-id transformations, monkeypatching platform user/group lookup to simulate existing and missing ids.

State and persistence: creates temp files/directories and writes ACLs. Monkeypatches platform uid/gid lookup functions.

Dependencies and integration points: depends on `borg.platform.acl_get`, `acl_set`, Linux ACL helper internals, shared skip markers, and platform user/group lookup. It supports ACL archive metadata portability.

Risks: ACL availability, fakeroot, and local user database strongly affect coverage. Non-ASCII ACL test requires a special local user and is commonly skipped.

Test signals: expected ACL byte substrings, exact access/default ACL bytes, fallback uid/gid conversion, and transformed ACL lines with appended ids.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/platform/linux_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/platform/platform_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/platform/platform_test.py

Purpose: shared platform-test helpers and basic process identity/liveness tests.

Important APIs and control flow: helper functions detect fakeroot, check if a username exists, and cache `are_acls_working()` by writing a temporary file and trying representative Darwin/Linux/FreeBSD ACL writes/reads. The module defines skip markers for OS, POSIX, fakeroot, ACL availability, Windows, and a specific non-ASCII user. Tests assert `process_alive` is true for current process identity, still true for host/tid variants that Borg treats as local-compatible, and false for a free PID; `test_process_id` validates tuple types, positive pid, non-empty hostname, and stable identity within a thread.

State and persistence: creates a temporary ACL probe file and uses cached result. Reads environment `FAKEROOTKEY` and local user database.

Dependencies and integration points: depends on platform flags, `acl_get`, `acl_set`, `get_process_id`, `process_alive`, testsuite `unopened_tempfile`, and the `free_pid` fixture from fslocking tests. Shared skip markers control OS-specific platform modules.

Risks: ACL probe behavior depends on filesystem and permissions. `free_pid` is inherently racy. Hostname/tid liveness semantics are Borg-specific and may differ from operating-system process APIs.

Test signals: skip-marker construction, current process liveness, dead PID non-liveness, and stable process id tuple.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/platform/platform_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/platform/windows_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/platform/windows_test.py

Purpose: Windows-only tests for `SyncFile` creation, text/binary writes, fd fallback, explicit sync, and write-through flag use.

Important APIs and control flow: module-level mark skips non-Windows. Tests write binary and text files through `SyncFile`, require `FileExistsError` for existing target, pass an existing file descriptor from `tempfile.mkstemp` to exercise base fallback behavior, call `.sync()`, and monkeypatch `borg.platform.windows._CreateFileW` to verify `FILE_FLAG_WRITE_THROUGH` in the sixth CreateFile argument.

State and persistence: creates temporary files and mutates Windows platform module function in-process.

Dependencies and integration points: depends on `SyncFile`, Windows-specific platform module constants/functions, pytest, and `tempfile`. It supports durable metadata writes on Windows.

Risks: exact CreateFileW argument position and flag value are Windows implementation details. Existing-file behavior differs from POSIX temp-file replacement flows.

Test signals: persisted file contents, expected existing-file exception, no sync exception, and observed write-through flag.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/platform/windows_test.py -->
