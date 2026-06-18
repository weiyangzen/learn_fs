# Group Research: group_277_cryptsetup_sources_block_storage_cryptsetup_lib_utils_c_sources_bloc_28f9002d6d7c

Scope: `Docs/research_subset_a.md`, source tree `sources/block-storage/cryptsetup`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils.c -->
# File Research: sources/block-storage/cryptsetup/lib/utils.c

## Purpose
General cryptsetup utility implementation for system sizing, process priority, keyfile reading, kernel version parsing, cipher usability checks, and Linux crypto API cipher-name conversion.

## Key Responsibilities
- Reports page size, online CPU count, total/free physical memory, and swap availability.
- Temporarily raises/restores process priority for expensive cryptographic operations.
- Reads passphrases/keyfiles from files or stdin with offset support, terminal rejection, newline stopping, safe allocation, and bounded default reads.
- Parses kernel version from `uname`.
- Tests cipher usability first through the storage backend and, for privileged callers, through temporary dm-crypt access.
- Converts `capi:` kernel crypto API cipher strings into cryptsetup cipher/integrity strings, including AEAD/authenc forms.

## Important Details
- Key material is allocated with `crypt_safe_alloc()` and wiped on failure.
- `keyfile_seek()` falls back to read-and-discard for non-seekable inputs such as pipes.
- Unlimited keyfile reads are still capped by `DEFAULT_KEYFILE_SIZE_MAXKB`.
- Cipher checks deliberately use random non-weak placeholder keys, not all-zero keys.
- `crypt_capi_to_cipher()` has careful bounded `sscanf`/`snprintf` handling for long crypto API strings.

## Dependencies
Uses `internal.h`, safe memory helpers, random generation, storage wrappers, dm/device metadata helpers, and low-level block I/O helpers.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_benchmark.c -->
# File Research: sources/block-storage/cryptsetup/lib/utils_benchmark.c

## Purpose
Implements public and internal benchmarks for ciphers and PBKDF settings.

## Key Responsibilities
- Allocates aligned benchmark buffers and random IV/key material.
- Measures kernel cipher encrypt/decrypt throughput through `crypt_cipher_perf_kernel()`.
- Benchmarks PBKDF2/Argon2 parameters through `crypt_pbkdf_perf()`.
- Lowers PBKDF memory cost when adjusted physical memory is below requested maximum.
- Raises process priority during PBKDF benchmarking and restores it afterward.
- Provides internal benchmark reuse rules for already-populated PBKDF settings.

## Important Details
- PBKDF2 is benchmarked for one second and then scaled to the requested target time.
- Argon2 benchmark results are reused if `iterations` is already set.
- `CRYPT_PBKDF_NO_BENCHMARK` requires explicit iterations or returns `-EINVAL`.
- The benchmark callback logs current memory, iteration, thread, and duration data.

## Dependencies
Uses crypto backend initialization, PBKDF limits/performance APIs, process-priority helper, and memory adjustment logic from `utils_pbkdf.c`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_benchmark.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_blkid.c -->
# File Research: sources/block-storage/cryptsetup/lib/utils_blkid.c

## Purpose
Provides an abstraction over libblkid probing and wiping so cryptsetup can detect and optionally erase filesystem, partition, and LUKS signatures.

## Key Responsibilities
- Creates blkid probe handles from paths or file descriptors.
- Configures probe chains for wipe detection, full printing, superblock-only detection, and fast detection.
- Filters LUKS superblocks in or out.
- Wraps normal and safe blkid probes into local `PRB_*` status values.
- Exposes detected partition/superblock type and superblock block size.
- Wipes detected magic signatures with libblkid wipe support or a manual fallback.

## Important Details
- The manual wipe fallback reads magic offsets/lengths from blkid values and writes zeros using aligned blockwise I/O.
- `blk_init_by_fd()` warns in the header that the file description offset is reset.
- When libblkid is unavailable, every API has a stub returning failure/unsupported values.
- Compatibility macros cover older blkid versions lacking wipe or bad-checksum flags.

## Dependencies
Depends on `utils_blkid.h`, `utils_io.h`, optional `<blkid/blkid.h>`, and blockwise write helpers.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_blkid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_blkid.h -->
# File Research: sources/block-storage/cryptsetup/lib/utils_blkid.h

## Purpose
Declares the local blkid probe wrapper interface.

## Key Responsibilities
- Forward-declares `struct blkid_handle`.
- Defines `blk_probe_status` values: `PRB_OK`, `PRB_EMPTY`, `PRB_AMBIGUOUS`, `PRB_FAIL`.
- Declares initialization, chain selection, LUKS filtering, probing, type accessors, wipe, support detection, and block-size lookup functions.

## Important Details
- Documents that fd-based initialization resets the file description offset.
- Keeps libblkid dependency out of most callers by hiding the concrete handle type.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_blkid.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_crypt.c -->
# File Research: sources/block-storage/cryptsetup/lib/utils_crypt.c

## Purpose
Implements cipher, integrity, PBKDF, and hex conversion utility logic.

## Key Responsibilities
- Parses cipher specs into cipher name, key count, and mode.
- Maps shorthand/default cipher modes such as `plain` and absent mode to `cbc-plain`.
- Parses integrity strings into kernel-style integrity mode names.
- Validates PBKDF names case-insensitively.
- Converts hex strings to bytes using constant-data-flow helper logic.
- Converts bytes to safe-allocated hex strings and logs bytes as hex.
- Detects `null`/`cipher_null` cipher specs.

## Important Details
- CAPI cipher names are treated specially because embedded dashes in driver names can be ambiguous.
- `crypt_hex_to_bytes()` optionally uses safe allocation for key material.
- `crypt_bytes_to_hex(0, ...)` returns `"-"` in a safe allocation.
- Integrity parser enforces key-size expectations for AEAD, HMAC, PHMAC, and CMAC modes.

## Dependencies
Uses public libcryptsetup constants, `utils_crypt.h`, safe memory allocation, and backend constant-time memory helpers.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_crypt.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_crypt.h -->
# File Research: sources/block-storage/cryptsetup/lib/utils_crypt.h

## Purpose
Declares cryptographic parsing and conversion helper APIs plus shared length limits.

## Key Responsibilities
- Defines cipher, keyfile, keyring, CAPI, and integrity string size limits.
- Declares cipher/mode, integrity, PBKDF, hex, logging, null-cipher, and CAPI conversion functions.

## Important Details
- The CAPI limits are sized for nested crypto API strings and bounded `sscanf` parsing.
- The header keeps helpers available to both library and CLI sources.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_crypt.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_device.c -->
# File Research: sources/block-storage/cryptsetup/lib/utils_device.c

## Purpose
Implements cryptsetup’s internal device abstraction for block devices, regular-file loop backing, direct I/O, topology, locking, sizing, and open-fd caching.

## Key Responsibilities
- Allocates and frees `struct device` instances.
- Detects whether paths are usable block devices or regular files requiring loop setup.
- Prefers direct I/O but falls back after a real read test when needed.
- Caches read-only/read-write fds and supports exclusive block-device opens.
- Tracks device block size, filesystem block size, physical block size, alignment, and loop block size.
- Attaches regular files to autoclear loop devices when needed.
- Checks device size/access, performs file growth, and calculates adjusted activation sizes.
- Reports topology alignment, read-ahead, rotational/DAX/zoned/NOP-DIF properties.
- Integrates metadata read/write locking via `utils_device_locking.c`.

## Important Details
- Regular files initially return `-ENOTBLK` from readiness checks so loop setup can be deferred.
- Direct I/O is validated with `read_lseek_blockwise()` on non-block devices.
- `device_block_adjust()` converts real device size to sectors and applies read-only activation flags.
- `device_is_identical()` compares block-device `st_rdev` or regular-file inode/device pairs.
- `device_internal_prepare()` requires root for loopback device use.
- Locked opens verify that the opened fd still corresponds to the locked resource.

## Dependencies
Uses Linux block ioctls, loop helpers, devpath/sysfs helpers, metadata locking, blockwise I/O, and libcryptsetup logging/error APIs.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_device.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_device_locking.c -->
# File Research: sources/block-storage/cryptsetup/lib/utils_device_locking.c

## Purpose
Implements on-disk/flock-based metadata locking for device and named resource serialization.

## Key Responsibilities
- Creates lock resource names by block-device major/minor or explicit resource name.
- Opens and creates the default LUKS2 lock directory safely.
- Acquires file, block-device, or name-based lock handles.
- Supports shared read locks and exclusive write locks with reference counts.
- Verifies lock resource identity after acquiring locks to handle races with deleted lock files.
- Removes name/block lock resource files when safe.
- Verifies that a locked device fd still matches the locked file or block-device resource.

## Important Details
- Regular file locks use the target file itself where possible, with an NFSv4 workaround.
- Block-device locks use separate files under `DEFAULT_LUKS2_LOCK_PATH`, keyed by `major:minor`.
- Named resource locks use `LN_<name>` files and can be blocking or nonblocking.
- Release logic takes an exclusive nonblocking lock and checks inode identity before unlinking resource files.
- Nested locks are refcounted for devices, but named `crypt_unlock_internal()` asserts no nested locks remain.

## Dependencies
Uses `flock`, openat/mkdirat, stat inode comparison, `utils_device_locking.h`, and device path/handle helpers.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_device_locking.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_device_locking.h -->
# File Research: sources/block-storage/cryptsetup/lib/utils_device_locking.h

## Purpose
Declares internal metadata locking primitives for devices and named resources.

## Key Responsibilities
- Exposes lock state queries.
- Declares internal read/write device lock and unlock functions.
- Declares locked-fd verification.
- Declares named write lock/unlock functions.
- Declares device lock-handle setters/getters used by `utils_device.c`.

## Important Details
- The API is internal and intentionally works with opaque `crypt_lock_handle` and `device` types.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_device_locking.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_devpath.c -->
# File Research: sources/block-storage/cryptsetup/lib/utils_devpath.c

## Purpose
Resolves Linux block-device paths and sysfs-derived device properties.

## Key Responsibilities
- Looks up `/dev` paths from `major:minor` device ids using `/sys/dev/block` first and recursive `/dev` scanning as fallback.
- Avoids exposing internal dm kernel names like `dm-X` when a mapper path is available.
- Reads numeric and string sysfs attributes.
- Detects partition number, partition status, partition start offset, rotational/DAX/zoned status, and NOP-DIF integrity profile.
- Finds a partition device by matching start/size under a base device.
- Finds the base disk for a partition.
- Looks up dm UUIDs through `/dev/disk/by-id` and `/sys/block/*/dm/uuid`.

## Important Details
- Old `/dev` scanning skips noisy top-level dirs and limits recursion depth.
- Device path verification checks block type and exact `st_rdev`; if mismatched, it falls back to scanning.
- DM devices are excluded from kernel partition lookup paths.
- NOP-DIF detection checks `integrity/format` and tries `metadata_bytes`, then `integrity/tag_size`.

## Dependencies
Uses `internal.h`, dm helper declarations from `utils_dm.h`, sysfs, `/dev`, and Linux major/minor macros.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_devpath.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_dm.h -->
# File Research: sources/block-storage/cryptsetup/lib/utils_dm.h

## Purpose
Declares cryptsetup’s internal device-mapper backend interface, target structures, and feature flags.

## Key Responsibilities
- Defines dm resume/suspend private flags and kernel-support feature flags.
- Defines dm target types: crypt, verity, integrity, linear, error, zero, unknown.
- Defines active-device query flags.
- Describes `struct dm_target` for crypt, verity, integrity, linear, and zero target parameters.
- Describes `struct crypt_dm_active_device` for active mapping state and target segment data.
- Declares target construction, dm create/reload/suspend/resume/remove/status/query helpers.
- Declares dm name, UUID, dependency, and devpath helper functions.

## Important Details
- Several feature flags encode kernel target capability detection, including verity FEC/signatures, integrity options, keyring keys, sector sizes, and workqueue options.
- `DM_INTEGRITY_DISCARDS_SUPPORTED` and `DM_INTEGRITY_RESIZE_SUPPORTED` share the same bit by design comment.
- `single_segment()` is a small helper for active-device segment checks.

## Dependencies
Forward-declares core cryptsetup structs and is consumed by activation, storage wrapper, verity, and devpath code.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_dm.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_io.c -->
# File Research: sources/block-storage/cryptsetup/lib/utils_io.c

## Purpose
Provides reliable read/write and aligned blockwise I/O helpers.

## Key Responsibilities
- Reads or writes exact buffer lengths while handling `EINTR`.
- Provides interruptible read/write variants controlled by a volatile quit flag.
- Performs blockwise writes and reads that preserve partial trailing blocks.
- Performs blockwise read/write at possibly unaligned logical offsets by padding the front block.
- Allocates aligned temporary buffers when caller buffers are not sufficiently aligned.

## Important Details
- `write_blockwise()` preserves trailing block content by reading the existing block, modifying the prefix, seeking back, and writing a full block.
- `read_blockwise()` reads full aligned blocks and copies partial trailing content out.
- `write_lseek_blockwise()` and `read_lseek_blockwise()` handle negative offsets relative to file end.
- Functions return byte counts or negative/error sentinel values rather than logging.

## Dependencies
Uses POSIX `read`, `write`, `lseek`, `posix_memalign`, and declarations from `utils_io.h`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_io.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_io.h -->
# File Research: sources/block-storage/cryptsetup/lib/utils_io.h

## Purpose
Declares cryptsetup’s low-level buffered and blockwise I/O helpers.

## Key Responsibilities
- Declares exact-length read/write helpers.
- Declares interruptible read/write helpers.
- Declares blockwise read/write helpers and lseek-plus-blockwise variants.

## Important Details
- The API passes block size and memory alignment explicitly, letting device code supply topology-derived values.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_io.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_keyring.c -->
# File Research: sources/block-storage/cryptsetup/lib/utils_keyring.c

## Purpose
Wraps Linux kernel keyring syscalls and provides parsing/lookup helpers for cryptsetup key descriptions.

## Key Responsibilities
- Maps local key types to Linux key type names.
- Wraps `request_key`, `add_key`, `keyctl describe/read/link/unlink`.
- Finds keys by type and description through `request_key()` or `/proc/keys` fallback.
- Adds keys to arbitrary or thread keyrings.
- Reads key payload size and payload into safe memory.
- Parses `%<type>:<desc>` key names and `@t`, `@p`, `@s`, etc. keyring aliases.
- Provides unsupported stubs when kernel keyring support is not compiled in.

## Important Details
- `/proc/keys` fallback validates descriptions with `KEYCTL_DESCRIBE` because key types can append suffixes after colons.
- `keyring_check()` probes logon key request behavior to detect syscall support.
- Payload reads allocate with `crypt_safe_alloc()`.
- `keyring_find_keyring_id_by_name()` only accepts keyring aliases, keyring type names, or numeric ids.

## Dependencies
Uses Linux keyctl syscalls directly, `utils_keyring.h`, safe memory helpers, and libcryptsetup constants.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_keyring.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_keyring.h -->
# File Research: sources/block-storage/cryptsetup/lib/utils_keyring.h

## Purpose
Declares kernel keyring wrapper types and APIs.

## Key Responsibilities
- Defines fallback `key_serial_t`.
- Defines supported key types: logon, user, big_key, trusted, encrypted, invalid.
- Declares type/name conversion, key lookup, keyring lookup, support check, request, read, add, and unlink functions.

## Important Details
- Keeps Linux keyring integration behind a small internal API so callers need not invoke syscalls directly.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_keyring.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_loop.c -->
# File Research: sources/block-storage/cryptsetup/lib/utils_loop.c

## Purpose
Implements loopback block-device helpers for regular-file-backed cryptsetup devices.

## Key Responsibilities
- Finds free loop devices through `/dev/loop-control`, falling back to scanning `/dev/loop0..255`.
- Attaches files to loop devices with `LOOP_CONFIGURE` when available.
- Falls back to older `LOOP_SET_FD` and `LOOP_SET_STATUS64`.
- Supports autoclear, read-only fallback, offset, and optional block-size setting.
- Detaches and resizes loop devices.
- Reads loop backing file from sysfs or `LOOP_GET_STATUS64`.
- Detects whether a path is a loop block device.

## Important Details
- Autoclear is verified after attach; failure clears the loop fd.
- The attach path returns an open loop fd so the loop remains alive until close.
- Read-only file attach is retried when write open fails with read-only/access errors.
- Loop-device detection checks block type and major number 7.

## Dependencies
Uses Linux loop ioctls, sysfs, major/minor helpers, and `utils_loop.h`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_loop.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_loop.h -->
# File Research: sources/block-storage/cryptsetup/lib/utils_loop.h

## Purpose
Declares loopback block-device helper APIs.

## Key Responsibilities
- Declares backing-file lookup, loop-device detection, attach, detach, and resize functions.

## Important Details
- `crypt_loop_attach()` returns an open loop fd on success and fills the selected loop path.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_loop.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_pbkdf.c -->
# File Research: sources/block-storage/cryptsetup/lib/utils_pbkdf.c

## Purpose
Defines default PBKDF settings and validates/initializes cryptsetup PBKDF configuration.

## Key Responsibilities
- Provides default PBKDF2, Argon2i, and Argon2id parameter structs.
- Selects defaults by PBKDF type or device type.
- Calculates adjusted usable physical memory for Argon2.
- Validates PBKDF type, hash, target time, iterations, memory, and parallelism.
- Enforces LUKS1/FIPS PBKDF2 restrictions.
- Initializes a crypt device’s PBKDF configuration, including string ownership.
- Limits benchmarked threads to online CPUs and memory to adjusted physical memory.
- Exposes public setters/getters for PBKDF type and iteration time.

## Important Details
- Small systems without swap get a stricter free-memory-based Argon2 cap.
- Forced no-benchmark values are not reduced by CPU or memory availability.
- Changing iteration time clears `CRYPT_PBKDF_NO_BENCHMARK` and resets iterations.
- PBKDF2 rejects memory/thread settings; Argon2 requires nonzero memory/thread settings.

## Dependencies
Uses `internal.h`, crypto backend hash/PBKDF limit APIs, system memory helpers, FIPS mode, and crypt device PBKDF state.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_pbkdf.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_safe_memory.c -->
# File Research: sources/block-storage/cryptsetup/lib/utils_safe_memory.c

## Purpose
Implements safe allocation, wipe, copy, free, realloc, and size lookup for sensitive memory.

## Key Responsibilities
- Provides explicit non-optimized memory zeroing through backend primitives.
- Provides backend copy helper to avoid sensitive register spill patterns.
- Allocates zeroed memory with a hidden metadata header.
- Attempts to `mlock()` safe allocations.
- Wipes and unlocks memory before free.
- Reallocates by allocating new safe memory, copying bounded old content, and freeing old memory.
- Returns stored safe allocation size.

## Important Details
- Allocation header records size and lock status before aligned data.
- `mlock()` failure is tolerated.
- `crypt_safe_free()` overwrites the stored size with a marker before freeing.
- Zero-size or overflow-prone allocations return `NULL`.

## Dependencies
Uses backend memory primitives from `internal.h` and POSIX `mlock`/`munlock`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_safe_memory.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_storage_wrappers.c -->
# File Research: sources/block-storage/cryptsetup/lib/utils_storage_wrappers.c

## Purpose
Provides a generic storage wrapper that can read/write raw data, userspace-encrypted data, or temporary dm-crypt-encrypted data through one interface.

## Key Responsibilities
- Initializes userspace crypto storage backends.
- Initializes temporary private dm-crypt mappings as fallback or requested backend.
- Opens underlying devices with direct/blockwise-aware parameters.
- Handles cipher-null as a no-op wrapper.
- Reads raw data, reads and decrypts data, decrypts an in-memory buffer, writes raw data, and encrypts then writes data.
- Destroys userspace backends or removes temporary dm devices.
- Exposes fdatasync and wrapper type.

## Important Details
- Data offsets must be sector-aligned for dm-crypt compatibility.
- Userspace backend can be rejected if it falls back to kernel crypto while `CSW_DISABLE_KCAPI` is set.
- Temporary dm names include pid and a static counter.
- For dm-crypt wrappers, I/O offsets are relative to the mapped device, not the original data offset.
- Wrapper destruction force-removes temporary dm mappings.

## Dependencies
Uses device abstraction, dm target creation/removal, volume keys, cipher parsing, storage backend APIs, and blockwise I/O helpers.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_storage_wrappers.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_storage_wrappers.h -->
# File Research: sources/block-storage/cryptsetup/lib/utils_storage_wrappers.h

## Purpose
Declares the generic storage wrapper interface.

## Key Responsibilities
- Defines flags controlling kernel crypto, dm-crypt fallback, read-only opens, large IVs, locked opens, and dm-crypt-only mode.
- Defines wrapper types: `NONE`, `USPACE`, and `DMCRYPT`.
- Declares initialization, destruction, raw/read-decrypt/decrypt/write/encrypt-write, datasync, and type accessor functions.

## Important Details
- Documents that all read/write offsets passed to wrapper functions are relative to `data_offset`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_storage_wrappers.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_wipe.c -->
# File Research: sources/block-storage/cryptsetup/lib/utils_wipe.c

## Purpose
Implements device wiping, including zero/random/special patterns and OPAL hardware erase integration.

## Key Responsibilities
- Uses `BLKZEROOUT` for block-device zero wipes when available.
- Implements the Gutmann special wipe pattern for rotational media.
- Writes wipe blocks with aligned blockwise I/O.
- Provides `crypt_wipe_device()` for internal device objects.
- Provides public `crypt_wipe()` for paths or the crypt device data device.
- Supports progress callbacks and interruption.
- Syncs devices after wiping.
- Implements OPAL PSID/factory reset or segment reset plus LUKS2 header-area wipe.

## Important Details
- All offsets, lengths, and wipe block sizes must be 512-byte aligned.
- Non-rotational devices downgrade special wipe to random wipe.
- Random wipe refreshes block contents each iteration.
- Zeroout ioctl availability is cached and disabled after first failure.
- OPAL segment wipe validates segment range and uses an exclusive OPAL lock.

## Dependencies
Uses device helpers, random generation, blockwise I/O, LUKS2 internals, and OPAL helper APIs.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/utils_wipe.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/verity/rs.h -->
# File Research: sources/block-storage/cryptsetup/lib/verity/rs.h

## Purpose
Declares Reed-Solomon codec structures and functions used by dm-verity FEC.

## Key Responsibilities
- Defines `data_t` byte symbols and the `struct rs` codec control block.
- Defines special zero index value `A0`.
- Provides `modnn()` field-index reduction helper.
- Declares RS context initialization/free plus 8-bit encode/decode functions.

## Important Details
- The structure stores Galois field lookup tables, generator polynomial, root count, primitive parameters, and shortened-block padding.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/verity/rs.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/verity/rs_decode_char.c -->
# File Research: sources/block-storage/cryptsetup/lib/verity/rs_decode_char.c

## Purpose
Implements byte-symbol Reed-Solomon decoding and correction based on libfec.

## Key Responsibilities
- Computes syndromes for the received RS block.
- Returns immediately when all syndromes are zero.
- Uses Berlekamp-Massey to compute the error locator polynomial.
- Uses Chien search to find error roots/locations.
- Computes the error evaluator polynomial.
- Applies corrections to the data block.
- Returns the number of corrected symbols or `-1` for uncorrectable errors.

## Important Details
- Rejects configurations with `nroots >= 256` due to fixed stack buffers.
- Location correction skips positions inside shortened padding.
- The function mutates the input data buffer in place.
- It expects an initialized `struct rs` with lookup tables from `init_rs_char()`.

## Dependencies
Uses `rs.h` and standard memory helpers.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/verity/rs_decode_char.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/verity/rs_encode_char.c -->
# File Research: sources/block-storage/cryptsetup/lib/verity/rs_encode_char.c

## Purpose
Initializes and frees Reed-Solomon contexts and encodes byte-symbol parity.

## Key Responsibilities
- Validates RS parameter ranges.
- Allocates and populates Galois field log/antilog tables.
- Verifies that the generator polynomial is primitive.
- Builds the RS generator polynomial from configured roots.
- Encodes data into parity bytes through feedback shift-register logic.
- Frees all RS lookup/generator allocations.

## Important Details
- Supports up to 8-bit symbols for `data_t`.
- `pad` implements shortened RS blocks.
- Generator polynomial is converted to index form for faster encoding.
- Encoding writes parity into caller-provided storage and does not allocate.

## Dependencies
Uses `rs.h` and standard allocation/memory functions.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/verity/rs_encode_char.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/verity/verity.c -->
# File Research: sources/block-storage/cryptsetup/lib/verity/verity.c

## Purpose
Implements dm-verity superblock read/write, parameter verification, activation, UUID generation, hash offset calculation, and metadata dump.

## Key Responsibilities
- Reads and validates the on-disk verity superblock.
- Writes normalized verity superblocks with lower-case hash algorithm names.
- Calculates hash-area offset in hash blocks.
- Generates verity UUIDs.
- Verifies verity data in userspace when requested and optionally attempts FEC repair.
- Activates dm-verity mappings through device-mapper.
- Loads root-hash signatures into the thread keyring for kernel activation.
- Dumps verity metadata and derived hash/FEC sizing.

## Important Details
- Superblock format follows the dm-verity documented `verity\0\0` signature structure.
- Headerless verity mode rejects superblock read/write.
- Read path updates loop block sizes for metadata and data devices based on header block sizes.
- Activation checks data/hash/fec device access and maps kernel unsupported cases to `-ENOTSUP`.
- Signature keys are unlinked from the thread keyring after activation attempt.

## Dependencies
Uses UUID library, dm target APIs, keyring APIs, device helpers, FEC/hash helpers, volume keys, and `internal.h`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/verity/verity.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/verity/verity.h -->
# File Research: sources/block-storage/cryptsetup/lib/verity/verity.h

## Purpose
Declares internal dm-verity handling APIs and constants.

## Key Responsibilities
- Defines maximum hash type and block-size validation macro.
- Declares superblock read/write.
- Declares activation, parameter verification, userspace verification, and hash creation.
- Declares FEC processing and size calculations.
- Declares hash offset/block calculations, UUID generation, and dump function.

## Important Details
- `VERITY_BLOCK_SIZE_OK(x)` returns true for invalid block sizes: not 512-multiple, too small, too large, or not power-of-two.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/verity/verity.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/verity/verity_fec.c -->
# File Research: sources/block-storage/cryptsetup/lib/verity/verity_fec.c

## Purpose
Implements dm-verity Forward Error Correction generation and verification/repair using Reed-Solomon codes.

## Key Responsibilities
- Validates FEC block-size and parity-root constraints.
- Computes interleaved RS byte offsets across protected input devices.
- Reads protected data and hash-area bytes into RS blocks.
- Encodes parity bytes to the FEC device or decodes parity for repair checking.
- Counts detected/corrected errors when requested.
- Computes the number of blocks covered by FEC and the number of RS parity blocks needed.

## Important Details
- FEC covers protected data plus hash area and optional padding/foreign metadata.
- If hash and FEC are the same device, coverage ends at `fec_area_offset`.
- If FEC is separate, coverage includes the hash device from hash offset to device end.
- FEC requires equal data and hash block sizes.
- RS parameters are 255-symbol blocks with roots constrained by min/max data symbol counts.

## Dependencies
Uses `verity.h`, `internal.h`, `rs.h`, device sizing/path helpers, and exact read/write buffer helpers.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/verity/verity_fec.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/verity/verity_hash.c -->
# File Research: sources/block-storage/cryptsetup/lib/verity/verity_hash.c

## Purpose
Creates and verifies dm-verity hash trees in userspace.

## Key Responsibilities
- Computes hash tree level counts, offsets, and sizes.
- Hashes data or lower hash levels with version-dependent salt ordering.
- Writes hash blocks with proper digest padding/spare zeroing.
- Verifies existing hash blocks and spare zero regions.
- Computes and verifies the root hash.
- Ensures hash device is large enough, growing regular-file metadata devices when allowed.
- Exposes total hash-block count calculation.

## Important Details
- Version 1 hashes salt before data; version 0 hashes salt after data.
- Digest slots for version 1 are padded to the next power-of-two digest size.
- Creation flushes the hash output file before reading it through a second handle for upper levels, for portability beyond Linux page cache behavior.
- Verification distinguishes data-area failure (`-EPERM`) from root-hash mismatch (`-EFAULT`).
- Warns if data block size exceeds kernel page size during creation.

## Dependencies
Uses crypt hash backend APIs, device helpers, overflow helpers, block sizing, and `verity.h`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/verity/verity_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/volumekey.c -->
# File Research: sources/block-storage/cryptsetup/lib/volumekey.c

## Purpose
Implements `struct volume_key` allocation, ownership, metadata, linked-list management, generation, and kernel-key upload/drop helpers.

## Key Responsibilities
- Allocates volume keys with safe memory for key bytes.
- Converts existing safe allocations into volume-key ownership.
- Replaces a volume key’s safe allocation with caller-provided safe memory.
- Provides accessors for key bytes, key length, id, description, keyring type, and linked-list next pointer.
- Adds keys to linked lists and finds keys by id.
- Frees entire linked lists, wiping key bytes.
- Generates random, normal, or empty quality volume keys.
- Uploads volume keys into the thread kernel keyring and drops uploaded keys.

## Important Details
- Key length zero is valid and represents no key bytes.
- Newly allocated keys start with `KEY_NOT_VERIFIED`, invalid keyring type, and key id `-1`.
- Description strings are owned copies.
- Kernel-key upload requires key bytes, description, and valid keyring type.

## Dependencies
Uses safe memory, random generation, keyring helpers, and internal cryptsetup unlink wrappers.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/volumekey.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/Makemodule.am -->
# File Research: sources/block-storage/cryptsetup/src/Makemodule.am

## Purpose
Defines automake build targets for the `cryptsetup`, `veritysetup`, and `integritysetup` command-line programs.

## Key Responsibilities
- Lists source files for each tool when its build conditional is enabled.
- Adds each enabled tool to `sbin_PROGRAMS`.
- Links each tool with `libcryptsetup.la` and relevant external libraries.
- Defines static variants when `STATIC_TOOLS` is enabled.
- Adds static crypto, pwquality, and devmapper libraries to static link lines where needed.

## Important Details
- All three tools share common utility sources: `lib/utils_crypt.c`, `lib/utils_loop.c`, `lib/utils_io.c`, `lib/utils_blkid.c`, and several `src/utils_*` files.
- `cryptsetup` links password quality libraries; `veritysetup` has a smaller dependency set; `integritysetup` links UUID and blkid.
- Static target source lists mirror their dynamic counterparts.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/Makemodule.am -->