# subset-b-008958 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/iaa/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/ext/compressors/iaa/CMakeLists.txt

Purpose: defines the WiredTiger IAA compression extension build. It exposes `HAVE_BUILTIN_EXTENSION_IAA` as a CMake boolean gated on `HAVE_LIBQPL`, rejects simultaneous builtin and dynamically loaded builds, builds the C++ `iaacodec` helper library when either IAA mode is enabled, then builds `wiredtiger_iaa` as an `OBJECT` target for builtin use or `MODULE` target for runtime extension loading.

Important APIs and integration: the target consumes WiredTiger generated headers, `src/include`, `iaacodec/include`, and Intel QPL via `wt::qpl`. Dynamic `ENABLE_IAA` builds install the module and link `CMAKE_DL_LIBS`; if libaccel-config is present it also links `wt::accel_config`. The static codec target is PIC so it can be embedded into the module or builtin extension.

State and persistence: no runtime state; it controls whether the persistent compression format can be produced/read by linking in `iaa_compress.c` and the C++ QPL bridge. Risks: build mode exclusivity is explicit, but QPL and optional accelerator configuration availability are external. Test signals include configuring both modes to assert the fatal path, configuring without QPL to assert dependency errors, and running extension compression tests on hardware and software fallback hosts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/iaa/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/iaa/iaa_compress.c -->
## sources/storage-engines/wiredtiger/ext/compressors/iaa/iaa_compress.c

Purpose: implements the C `WT_COMPRESSOR` adapter named `iaa`, bridging WiredTiger's compressor callbacks to the C-compatible IAA codec functions in `iaaInterface-c.h`.

Important APIs/types/functions: `iaa_COMPRESSOR` embeds `WT_COMPRESSOR` first and stores `WT_EXTENSION_API`. `iaa_compress` calls `doCompressData`, sets `compression_failed` and `result_lenp` on nonzero output, and reports `WT_ERROR` through `iaa_error` otherwise. `iaa_decompress` calls `doDecompressData` and treats nonzero result length as success. `iaa_pre_size` delegates to `getMaxCompressedDataSize`; `iaa_add_compressor` registers callbacks with `connection->add_compressor`; `iaa_extension_init` and conditionally exported `wiredtiger_extension_init` handle builtin vs module integration.

Control flow and state: initialization allocates one compressor object per connection and frees it on `terminate`. Data persistence is the QPL gzip-mode deflate stream produced by the codec; this file stores no extra prefix. Risks: all lengths are cast to `uint32_t`, so the implementation assumes WiredTiger never asks this extension to process buffers above 4 GiB. Success is inferred from result length, which makes zero-length compression/decompression ambiguous. Test signals should include round trips, incompressible data, destination-too-small behavior, corrupt input, empty input, builtin symbol collision checks, and software fallback on hosts without IAA hardware.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/iaa/iaa_compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/iaa/iaacodec/include/IAACompressionCodecDeflate.h -->
## sources/storage-engines/wiredtiger/ext/compressors/iaa/iaacodec/include/IAACompressionCodecDeflate.h

Purpose: declares the C++ IAA/QPL deflate codec used behind the C extension. The namespace `DB::IAA` contains hardware job pooling, software fallback, hardware codec, and aggregate codec classes.

Important APIs/types/functions: `DeflateJobHWPool` is a singleton with `jobPoolSize = 256`, static `qpl_job *jobPool[]`, static atomic locks, `acquireJob`, `releaseJob`, and `jobPoolReady`. `SoftwareCodecDeflate` owns one software `qpl_job` through `jobSWbuffer`. `HardwareCodecDeflate` exposes `hwEnabled`, page-touching `memPageSet`, and hardware compress/decompress calls. `CompressionCodecDeflate` owns both codecs and exposes `doCompressData`, `doDecompressData`, and `getMaxCompressedDataSize`.

Control flow and state: job-pool state is process-global for the hardware path; software job state is per `SoftwareCodecDeflate` object. The aggregate class tries hardware first when enabled and falls back to software on a zero result. Dependencies are QPL, C++ atomics, WiredTiger callback types, and x86 headers. Risks include busy-waiting during pool destruction, failure paths that can leave partially initialized pool entries, range assumptions in `job_id` conversion, and hardware fallback conflating legitimate zero-byte output with failure. Test signals include concurrent job acquisition/release, pool exhaustion, constructor failure fallback, and QPL status failure injection.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/iaa/iaacodec/include/IAACompressionCodecDeflate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/iaa/iaacodec/include/iaaInterface-c.h -->
## sources/storage-engines/wiredtiger/ext/compressors/iaa/iaacodec/include/iaaInterface-c.h

Purpose: provides the C ABI for the C compressor adapter to call the C++ IAA codec without exposing C++ symbols or types beyond WiredTiger pointers.

Important APIs: `getMaxCompressedDataSize`, `doCompressData`, and `doDecompressData` are declared in an `extern "C"` block when compiled under C++. They accept `WT_COMPRESSOR *`, `WT_SESSION *`, raw byte buffers, `uint32_t` sizes, and an optional decompression result pointer.

Control flow and state: this header has no state, but its ABI enforces the 32-bit length contract used by both the C adapter and C++ codec. Integration points are `iaa_compress.c` and `iaaInterface-c.cpp`. Risks are ABI drift, C/C++ include compatibility, and truncation if callers pass sizes wider than `uint32_t`. Test signals are compile/link tests from C and C++, plus compressor round trips through the exported C functions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/iaa/iaacodec/include/iaaInterface-c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/iaa/iaacodec/src/IAACompressionCodecDeflate.cpp -->
## sources/storage-engines/wiredtiger/ext/compressors/iaa/iaacodec/src/IAACompressionCodecDeflate.cpp

Purpose: implements IAA/QPL deflate compression and decompression. It initializes a hardware QPL job pool, falls back to QPL software jobs, and uses gzip-mode dynamic-Huffman deflate streams.

Important functions: `DeflateJobHWPool::instance` provides a static singleton. The constructor logs QPL version and attempts `initJobPool`; the destructor calls `destroyJobPool`. `HardwareCodecDeflate::doCompressData` and `doDecompressData` acquire a job, populate `qpl_job`, touch output pages, execute, and release. `SoftwareCodecDeflate::getJobCodecPtr` lazily initializes a software job. `CompressionCodecDeflate` chooses hardware then software and computes a zlib-compatible deflate bound.

Control flow and state: hardware jobs are shared across threads using atomic locks; software jobs are owned by each codec instance. `iaa_message` logs through WiredTiger when compressor/session are available and also prints to stdout. Persistent output is QPL gzip-mode compressed data. Risks: QPL init errors in the software path are mostly ignored before job use; hardware pool init can leak earlier jobs on mid-loop failure; `destroyJobPool` spin-waits; stdout logging from an extension can surprise embedding applications; status errors collapse into zero length. Tests should cover hardware success, software fallback, QPL error returns, pool contention, corrupt compressed streams, and exact compressed-bound sizing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/iaa/iaacodec/src/IAACompressionCodecDeflate.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/iaa/iaacodec/src/iaaInterface-c.cpp -->
## sources/storage-engines/wiredtiger/ext/compressors/iaa/iaacodec/src/iaaInterface-c.cpp

Purpose: implements the C ABI declared by `iaaInterface-c.h` by wrapping a `thread_local DB::IAA::CompressionCodecDeflate`.

Important APIs/functions: `getMaxCompressedDataSize` uses a default-constructed thread-local codec. `doCompressData` and `doDecompressData` use thread-local codecs constructed with the first `WT_COMPRESSOR` and `WT_SESSION` seen by that thread, then delegate to the aggregate codec.

Control flow and state: codec state is per thread and lives until thread exit. This caches QPL software job state per thread and shares hardware jobs globally through the pool. Integration is the narrow bridge from `iaa_compress.c`. Risks: the first compressor/session pointers captured for a thread are used for later calls on that thread, which mainly affects logging and initialization context; thread-local lifetime can outlive WiredTiger connection teardown if host thread reuse is unusual. Tests should include repeated calls across multiple sessions on the same thread, multiple threads, teardown/reload, and fallback after hardware acquisition failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/iaa/iaacodec/src/iaaInterface-c.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/lz4/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/ext/compressors/lz4/CMakeLists.txt

Purpose: defines the LZ4 compressor build. `HAVE_BUILTIN_EXTENSION_LZ4` is gated on `HAVE_LIBLZ4`; builtin and dynamic `ENABLE_LZ4` are mutually exclusive.

Integration: builds `wiredtiger_lz4` from `lz4_compress.c` as either `OBJECT` for builtin use or `MODULE` for loadable extension use. It includes WiredTiger generated/config headers, links `wt::lz4`, applies C diagnostic flags, marks the target PIC, and installs only when `ENABLE_LZ4` is on.

State: no runtime state. Risks are dependency discovery and keeping builtin/module symbol behavior aligned with `lz4_compress.c`. Test signals include configuring dependency-missing builds, builtin builds, module builds, and installation layout checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/lz4/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/lz4/lz4_compress.c -->
## sources/storage-engines/wiredtiger/ext/compressors/lz4/lz4_compress.c

Purpose: implements WiredTiger's LZ4 compressor extension and preserves backward compatibility for old raw-compression objects.

Important APIs/types/functions: `LZ4_COMPRESSOR` stores extension API state. `LZ4_PREFIX` is a 16-byte little-endian header containing true compressed length, true uncompressed length, useful decompressed length, and reserved zero. Big-endian builds byte-swap with `lz4_prefix_swap`. `lz4_compress` writes compressed data after the prefix and only succeeds when compressed output plus prefix is smaller than source. `lz4_decompress` validates stored size, optionally uses `scr_alloc` as a bounce buffer for legacy raw-compression cases, and verifies decoded bytes equal `useful_len`. `lz_add_compressor` registers both `lz4` and `lz4-noraw`.

State and persistence: compressed blocks persist an LZ4 raw block plus the prefix. The compressor object is per connection and freed on terminate. Risks: prefix corruption must be caught before decompression; the legacy bounce-buffer path can allocate `prefix.uncompressed_len`; size casts to `int` follow library ABI limits; `lz4-noraw` is compatibility surface. Test signals include endian-prefix tests, corrupt prefix lengths, truncated input, bounce-buffer legacy objects, incompressible data marking `compression_failed`, and both registered names.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/lz4/lz4_compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/nop/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/ext/compressors/nop/CMakeLists.txt

Purpose: builds the sample no-op compressor as `wiredtiger_nop_compress` from `nop_compress.c`.

Integration: this is always a shared library target rather than a builtin-configurable target. It includes WiredTiger source/generated/config headers and applies C diagnostic flags. It does not link a third-party compression library.

State: no build-time persistence. Risks are mostly sample-extension drift from the current `WT_COMPRESSOR` ABI and absence of install logic in this file. Test signals are module load and a pass-through compression/decompression round trip.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/nop/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/nop/nop_compress.c -->
## sources/storage-engines/wiredtiger/ext/compressors/nop/nop_compress.c

Purpose: sample `WT_COMPRESSOR` implementation that copies data unchanged while exercising the compressor extension API.

Important APIs/types/functions: `NOP_COMPRESSOR` embeds `WT_COMPRESSOR`, stores `WT_EXTENSION_API`, and counts calls. `nop_compress` copies `src` to `dst` when capacity permits and sets `compression_failed` on short destination. `nop_decompress` copies `dst_len` bytes from source to destination and reports `dst_len`. `nop_pre_size` returns `src_len`. `wiredtiger_extension_init` allocates the compressor and registers it as `nop`.

State and persistence: call count lives in the compressor object only; persisted bytes are identical to input. Risks: `nop_decompress` trusts WiredTiger's expected output length and does not independently verify `src_len >= dst_len`; this is acceptable for an example but not defensive against corrupt inputs. Tests should cover load/unload, destination-too-small compression, pass-through round trips, and terminate freeing the heap object.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/nop/nop_compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/snappy/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/ext/compressors/snappy/CMakeLists.txt

Purpose: defines the Snappy compressor build with builtin and dynamic modes.

Integration: `HAVE_BUILTIN_EXTENSION_SNAPPY` depends on `HAVE_LIBSNAPPY`; builtin and `ENABLE_SNAPPY` are mutually exclusive. The build creates `wiredtiger_snappy` as `OBJECT` or `MODULE`, includes WiredTiger headers, links `wt::snappy`, applies C diagnostics, sets PIC, and installs in dynamic-extension mode.

State: none at build time. Risks are dependency detection and keeping module/builtin export decisions aligned with the C source. Test signals include configure-time dependency failure, builtin symbol exclusion, module installation, and load-time Snappy round trips.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/snappy/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/snappy/snappy_compress.c -->
## sources/storage-engines/wiredtiger/ext/compressors/snappy/snappy_compress.c

Purpose: implements the WiredTiger Snappy compressor and stores the exact compressed byte count required by Snappy decompression.

Important APIs/functions: `SNAPPY_COMPRESSOR` stores the extension API. `SNAPPY_PREFIX` is an eight-byte little-endian compressed-length prefix. `snappy_compression` compresses after the prefix, succeeds only if output plus prefix is smaller than source, writes the prefix, and sets `compression_failed` otherwise. `snappy_decompression` reads and byte-swaps the prefix as needed, validates it against `src_len`, calls `snappy_uncompress`, and returns the produced length. `snappy_error` maps `snappy_status` to extension errors.

State and persistence: persisted blocks are prefix plus Snappy stream. Compressor allocation is per connection and freed on terminate. Risks: prefix load/store uses direct `uint64_t *` casts, which can be sensitive to alignment on strict platforms; decompression depends on prefix integrity; Snappy status errors are converted to `WT_ERROR`. Tests should cover endian behavior, corrupt/truncated prefixes, incompressible data, invalid Snappy payloads, and builtin vs loadable init symbols.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/snappy/snappy_compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/zlib/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/ext/compressors/zlib/CMakeLists.txt

Purpose: defines the zlib compressor build.

Integration: `HAVE_BUILTIN_EXTENSION_ZLIB` depends on `HAVE_LIBZ` and conflicts with `ENABLE_ZLIB`. The target `wiredtiger_zlib` is an `OBJECT` builtin or loadable `MODULE`, includes WiredTiger headers, links `wt::zlib`, applies C diagnostics, sets PIC, and installs only for dynamic extension builds.

State: no runtime state in CMake. Risks are dependency discovery and export-mode consistency. Test signals include configure failure without zlib, dynamic install checks, builtin link checks, and zlib compression-level config tests in the C file.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/zlib/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/zlib/zlib_compress.c -->
## sources/storage-engines/wiredtiger/ext/compressors/zlib/zlib_compress.c

Purpose: implements WiredTiger's zlib compressor extension with optional `compression_level` configuration.

Important APIs/types/functions: `ZLIB_COMPRESSOR` stores extension API and compression level. `ZLIB_OPAQUE` lets zlib callbacks allocate/free scratch memory through WiredTiger `scr_alloc` and `scr_free`. `zlib_compress` initializes a z_stream, runs `deflate(..., Z_FINISH)`, marks compression failure if the stream does not finish, then ends the stream. `zlib_decompress` inflates until completion and reports `total_out`. `zlib_init_config` accepts levels 0 through 9. `zlib_extension_init` registers both `zlib` and `zlib-noraw`.

State and persistence: no custom prefix; persisted bytes are zlib stream output. Compressor state is per connection. Risks: `pre_size` is NULL, so sizing relies on WiredTiger's generic handling; `avail_in/out` are cast to `uint32_t`; decompression loops until `inflate` stops and trusts zlib to catch corruption; raw-compat registration expands API surface. Tests should cover all valid compression levels, invalid level rejection, custom allocator failure, truncated streams, incompressible data, and both compressor names.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/zlib/zlib_compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/zstd/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/ext/compressors/zstd/CMakeLists.txt

Purpose: defines the Zstandard compressor build.

Integration: `HAVE_BUILTIN_EXTENSION_ZSTD` depends on `HAVE_LIBZSTD`; builtin and `ENABLE_ZSTD` are mutually exclusive. It builds `wiredtiger_zstd` as builtin `OBJECT` or dynamic `MODULE`, includes WiredTiger headers, links `wt::zstd`, applies C diagnostics, sets PIC, and installs the dynamic target.

State: no runtime state here. Risks are dependency discovery and symbol/export mode consistency. Test signals include configure-time dependency failures, builtin/dynamic builds, and extension load with context-pool initialization from `zstd_compress.c`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/zstd/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/zstd/zstd_compress.c -->
## sources/storage-engines/wiredtiger/ext/compressors/zstd/zstd_compress.c

Purpose: implements WiredTiger's Zstandard compressor with pooled compression/decompression contexts.

Important APIs/types/functions: `ZSTD_CONTEXT_POOL` holds a spinlock and free list of `ZSTD_CONTEXT` wrappers. `ZSTD_COMPRESSOR` stores compression level plus separate pools for `ZSTD_CCtx` and `ZSTD_DCtx`. `zstd_compress` gets a context if available, writes compressed data after an eight-byte little-endian length prefix, and succeeds only when smaller than input. `zstd_decompress` validates the stored length and uses a pooled or temporary decompression context. `zstd_pre_size` returns `ZSTD_compressBound + prefix`. `zstd_init_context_pool` creates 50 contexts by default; terminate frees pools and destroys spinlocks.

State and persistence: persisted blocks are prefix plus zstd payload. Runtime state includes two context pools guarded by WiredTiger spinlocks. Risks: `zstd_extension_init` does not check return values from `zstd_init_context_pool`, so allocation/context-creation failures can leave null pools that later code assumes exist; partial pool-init failures can leak objects; compression level is accepted without range validation; direct prefix `uint64_t *` access may be alignment-sensitive. Tests should include context-pool exhaustion, fallback path when no context is free, pool init failure, corrupt prefixes, high/low compression levels, and terminate under active-use constraints.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/compressors/zstd/zstd_compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/encryptors/nop/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/ext/encryptors/nop/CMakeLists.txt

Purpose: builds the sample no-op encryptor as a loadable module from `nop_encrypt.c`.

Integration: creates `wiredtiger_nop_encrypt` as a `MODULE`, includes WiredTiger source/generated/config headers, and applies C diagnostic flags. It has no third-party crypto dependency and no builtin-mode configuration.

State: no runtime state here. Risks are sample-extension ABI drift and lack of install logic in this file. Test signals include module load, `add_encryptor("nop")`, and pass-through encrypt/decrypt behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/encryptors/nop/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/encryptors/nop/nop_encrypt.c -->
## sources/storage-engines/wiredtiger/ext/encryptors/nop/nop_encrypt.c

Purpose: sample `WT_ENCRYPTOR` implementation that copies bytes unchanged while demonstrating encryptor customization.

Important APIs/functions: `NOP_ENCRYPTOR` embeds `WT_ENCRYPTOR`, stores extension API, and counts calls. `nop_encrypt` checks destination capacity and copies source. `nop_decrypt` copies `dst_len` bytes and reports that length. `nop_sizing` reports zero expansion. `nop_customize` copies the encryptor, reads `keyid` and `secretkey`, rejects specifying both, allows neither for tests, and does not install real key material. `wiredtiger_extension_init` registers `nop`.

State and persistence: customized encryptor instances are heap objects; no persistent format overhead because ciphertext equals plaintext. Risks: this is not encryption; decrypt trusts caller-provided output length; keys are parsed only as demonstration. Tests should cover customize with keyid, secretkey, both, neither, capacity errors, pass-through round trips, and terminate of customized and original instances.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/encryptors/nop/nop_encrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/encryptors/rotn/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/ext/encryptors/rotn/CMakeLists.txt

Purpose: builds the ROT-N/Vigenere demonstration encryptor.

Integration: creates `wiredtiger_rotn` as a loadable `MODULE`, includes WiredTiger headers, and applies C diagnostic flags. It has no external crypto dependency and no builtin build mode.

State: no runtime state in CMake. Risks are example-only crypto being accidentally mistaken for secure encryption. Test signals include module loading and configuration paths handled by `rotn_encrypt.c`, especially `rotn_force_error`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/encryptors/rotn/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/encryptors/rotn/rotn_encrypt.c -->
## sources/storage-engines/wiredtiger/ext/encryptors/rotn/rotn_encrypt.c

Purpose: demonstration/test encryptor implementing ROT-N without a secret key and a Vigenere-like byte shift when `secretkey` is configured. The file explicitly warns that it provides no real security.

Important APIs/types/functions: `ROTN_ENCRYPTOR` stores `rot_N`, copied key strings, forward/backward shift arrays, and `force_error`. Constants define a 4-byte checksum and 16-byte IV expansion. `rotn_encrypt` writes dummy checksum and IV, copies plaintext, then rotates alphabetic characters or shifts all bytes. `rotn_decrypt` strips the header and reverses the transform, optionally returning `-1000` for testing. `rotn_sizing` reports 20 bytes of expansion. `rotn_customize` parses `keyid` and alphabetic `secretkey`, builds shift arrays, and sets `rot_N`. `rotn_configure` handles `rotn_force_error`.

State and persistence: encrypted blocks persist `CCCC` checksum, `IIII...` IV, and transformed data. Customized encryptors own allocated key/shift arrays and free them on terminate. Risks: checksum and IV are constants, keyid uses `atoi` so nonnumeric prefixes can be accepted as zero, decrypt can underflow if input is shorter than the fixed header, and encrypt reports `dst_len` rather than the actual required length if overallocated. Tests should cover ROT and Vigenere round trips, invalid secret characters, forced decrypt errors, short ciphertext, sizing, and cleanup after customize failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/encryptors/rotn/rotn_encrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/encryptors/sodium/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/ext/encryptors/sodium/CMakeLists.txt

Purpose: defines the libsodium encryptor build.

Integration: `HAVE_BUILTIN_EXTENSION_SODIUM` depends on `HAVE_LIBSODIUM`, conflicts with `ENABLE_SODIUM`, and builds `wiredtiger_sodium` as builtin `OBJECT` or loadable `MODULE`. The target includes WiredTiger headers, links `wt::sodium`, applies diagnostics, sets PIC, and installs dynamic builds.

State: none here. Risks include a minor diagnostic typo in the fatal-error string and dependency availability. Test signals include dependency-missing configuration, builtin/dynamic builds, installation, and runtime key handling in `sodium_encrypt.c`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/encryptors/sodium/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/encryptors/sodium/sodium_encrypt.c -->
## sources/storage-engines/wiredtiger/ext/encryptors/sodium/sodium_encrypt.c

Purpose: real at-rest encryption extension using libsodium's XChaCha20-Poly1305 AEAD construction. It is scoped to protecting a shut-down database at rest, not live-memory compromise.

Important APIs/types/functions: constants define key, nonce, MAC, and 4-byte header lengths. `SODIUM_ENCRYPTOR` stores the secret key allocated with `sodium_malloc`. `sodium_encrypt` writes a version/construction header, random nonce, and AEAD ciphertext+tag using the header as associated data. `sodium_decrypt` verifies and decrypts using the header and nonce. `sodium_sizing` reports constant expansion. `sodium_customize` rejects simultaneous `keyid` and `secretkey`, requires one, rejects keyid because key services are unsupported, decodes a 64-character hex key, and validates `KEY_LEN`. `wiredtiger_extension_init` calls `sodium_init` and registers `sodium`.

State and persistence: persistent format is header, nonce, ciphertext, authentication tag. Per-key customized encryptors hold secret key memory until `sodium_terminate`, which calls `randombytes_close`, `sodium_free`, and `free`. Risks: decrypt length arithmetic can underflow for inputs shorter than header+nonce; there is no explicit pre-decrypt header version/construction validation beyond AEAD authentication over supplied header; key material remains in process memory while open; keyid services are not implemented. Tests should include valid key round trips, non-hex and wrong-length keys, rejected keyid, tampered header/nonce/ciphertext, short ciphertext, sizing, and repeated customize/terminate cycles.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/encryptors/sodium/sodium_encrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/page_log/palite/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/ext/page_log/palite/CMakeLists.txt

Purpose: builds `wiredtiger_palite`, a C++20 SQLite-backed implementation of WiredTiger's page log interface.

Integration: checks compiler support with minimum GNU 13, Clang 17, or MSVC 16.10, warns and returns when too old, then sets C++20 without extensions. The module links `wt::sqlite3`, includes WiredTiger headers, and applies C++ diagnostics. Linux builds add `-z,nodelete` and `--exclude-libs,ALL` to avoid sanitizer/library lifetime and symbol issues. Darwin builds run `dsymutil` after build.

State: no runtime state here, but the build controls availability of the persistent PALite SQLite backend. Risks include compiler-version variable assumptions, silently skipping the build on older compilers, and platform-specific linker behavior. Test signals include compiler-gated configure tests, Linux sanitizer builds, macOS dSYM generation, and loading the module with SQLite linked.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/page_log/palite/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/page_log/palite/palite.cpp -->
## sources/storage-engines/wiredtiger/ext/page_log/palite/palite.cpp

Purpose: implements `WT_PAGE_LOG` using SQLite databases. PALite stores global LSN/table metadata in `globals.db`, checkpoints in `checkpoints.db`, and page records in 17 sharded `pages_NN.db` files under `kv_home`.

Important APIs/types/functions: `Config` parses extension config and `WT_PALITE_CONFIG` for home, cache/mmap sizes, simulated delays/errors, materialization delay, logging, SQL tracing, and verification. `safe_call` maps C++ exceptions to WiredTiger error codes for C callbacks. `SQLiteCall` wraps SQLite calls, tracing, retrying busy/locked operations, and translating errors. `Connection` owns per-thread SQLite connections and prepared statements. `Table<Traits>` provides per-table readers-writer locking and per-thread connection maps. `Globals`, `Checkpoints`, and `Pages` define schemas and SQL. `Storage` coordinates tables, shards, LSN allocation, object counters, checkpoint abandon, and simulated network behavior. `PaliteHandle` implements per-table handle callbacks; `Palite` implements service-level callbacks and registers as `palite`.

Control flow: extension init constructs `Palite`, initializes `kv_home`, reads the last LSN, and calls `connection->add_page_log`. Opening a table handle records the table ID and opens the shard. `put` simulates network behavior, allocates a new global LSN, inserts a full/delta page, optionally verifies the delta chain, and returns the LSN. `get` selects materialized pages at or below the requested LSN, stops at a full page, verifies the chain, reverses results to full-page-first order, and fills args. `discard` writes a special discarded delta. `complete_checkpoint` allocates an LSN and inserts checkpoint metadata. `get_complete_checkpoint` returns the latest checkpoint. `abandon_checkpoint` obtains a storage-wide exclusive lock, finds the latest checkpoint, and deletes checkpoint/page records with LSN greater than that checkpoint. `trim_table` is intentionally a no-op apart from generating an LSN.

State and persistence: SQLite WAL mode is used with synchronous=NORMAL, memory temp store, mmap/cache tuning, page-size tuning for page shards, and per-thread non-shared connections opened with `SQLITE_OPEN_NOMUTEX`. The `pages` table persists table/page/LSN/backlink/base/flags/materialization timestamp/page data, plus generated `delta` and `discarded` columns. A partial unique index on `(table_id, page_id, backlink_lsn)` for non-discarded deltas replaces failed delta writes. Risks: multi-process access is explicitly unsupported; `last_materialized_lsn` is set but not used in page visibility; materialization delay uses steady-clock timestamps persisted to SQLite, which are process-relative; abandoning a checkpoint deletes records above the checkpoint but does not decrement global LSN; result array capacity errors throw; short or inconsistent delta chains are fatal. Test signals include crash/reopen with existing SQLite files, concurrent table/page access across shards, busy/locked retry behavior, full/delta/discard chain verification, failed delta replacement, checkpoint complete/retrieve/abandon, delayed materialization visibility, simulated network errors, and module teardown with outstanding references.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/page_log/palite/palite.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/storage_sources/dir_store/CMakeLists.txt -->
## sources/storage-engines/wiredtiger/ext/storage_sources/dir_store/CMakeLists.txt

Purpose: builds the directory-backed storage source extension target `wiredtiger_dir_store` from `dir_store.c`.

Integration: the target is a loadable `MODULE`, includes WiredTiger source/generated/config headers, and applies C diagnostic flags. This CMake file is the build entry point for the storage-source implementation but does not include install or builtin-mode logic.

State and persistence: no runtime state here; persistence behavior belongs to `dir_store.c`, which is outside this work item. Risks are target/source drift and module-only availability. Test signals include building the module, loading it through WiredTiger's storage source extension path, and verifying the target sees generated config headers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/storage_sources/dir_store/CMakeLists.txt -->
