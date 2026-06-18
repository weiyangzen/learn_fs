# Research Group subset-b-000242

This grouped report covers libostree autocleanup declarations, blob readers, bloom filters, bootconfig parsing, bootloader backends, stream adapters, private command vtables, content writing, and core object-format helpers. Each file section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-autocleanups.h -->
# sources/cloud-native/ostree/src/libostree/ostree-autocleanups.h

## Purpose
Defines GLib `g_autoptr`, `g_auto`, and `g_autofree` cleanup hooks for exported OSTree types when building libostree or when the consuming GLib is new enough to expose cleanup support. It lets callers use automatic stack cleanup for common libostree objects without hand-written `goto out` cleanup blocks.

## Important APIs and Types
The file declares cleanup functions for refcounted objects such as `OstreeAsyncProgress`, `OstreeBootconfigParser`, `OstreeDeployment`, `OstreeMutableTree`, `OstreeRepo`, `OstreeRepoFile`, `OstreeSePolicy`, `OstreeSysroot`, and `OstreeSysrootUpgrader`, plus boxed/manual types such as `OstreeDiffItem`, `OstreeRepoCommitModifier`, `OstreeRepoDevInoCache`, `OstreeCommitSizesEntry`, `OstreeKernelArgs`, `OstreeCollectionRef`, `OstreeRemote`, and `OstreeRepoFinderResult`. It also defines clear/free cleanup for `OstreeRepoCommitTraverseIter`, `OstreeCollectionRefv`, and `OstreeRepoFinderResultv`.

## Control Flow
There is no runtime control flow. The only branch is a preprocessor guard: cleanup macros are exposed during `OSTREE_COMPILATION` or for GLib 2.44 and newer.

## State and Persistence
No state is stored. The cleanup hooks affect ownership discipline at call sites and prevent leaks during early returns.

## Dependencies and Integration Points
Includes `<ostree.h>` and depends on each type's corresponding free, unref, or clear function. It is included by public and internal libostree code that wants GLib automatic cleanup syntax.

## Risks
The guard avoids exporting libglnx cleanup backports to old-GLib consumers, which is important ABI/API hygiene. Adding a type here requires choosing the exact matching destructor; a wrong cleanup function can cause leaks, double frees, or missed finalization.

## Test Signals
Compile tests with supported minimum GLib and modern GLib are the main signal. Leak-checking code paths that use `g_autoptr(OstreeRepo)` and related cleanup declarations verifies destructor pairing.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-autocleanups.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-base64.c -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader-base64.c

## Purpose
Implements `OstreeBlobReaderBase64`, a final `GDataInputStream` subclass that implements `OstreeBlobReader` by reading one newline-delimited base64 blob at a time.

## Important APIs and Types
`_ostree_blob_reader_base64_new()` constructs the reader around a base stream using the `base-stream` property inherited from `GDataInputStream`. `ostree_blob_reader_base64_read_blob()` is the interface implementation and returns a decoded `GBytes` for the next line.

## Control Flow
The interface initializer assigns `iface->read_blob`. On each read, the code calls `g_data_input_stream_read_line()`, propagates I/O errors, returns `NULL` on EOF, decodes the line in place with `g_base64_decode_inplace()`, clears the now-unused trailing encoded bytes with `explicit_bzero()`, and transfers the buffer into `GBytes`.

## State and Persistence
The only persistent state is the underlying stream cursor. Decoded data is returned as owned bytes; no blob cache is kept.

## Dependencies and Integration Points
Depends on `ostree-blob-reader-base64.h`, GLib/GIO stream APIs, and the shared `OstreeBlobReader` interface. It integrates with consumers that need line-oriented base64 signature/key/blob input.

## Risks
Malformed base64 handling is delegated to GLib's decoder; callers must distinguish EOF from error by checking the `GError`. Because one blob equals one input line, embedded newlines in encoded data are not supported here.

## Test Signals
Tests should cover valid base64 lines, EOF after last line, read cancellation/error propagation, invalid base64 behavior, and ensuring no trailing decoded buffer bytes leak into the returned `GBytes`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-base64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-base64.h -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader-base64.h

## Purpose
Declares the base64 blob reader implementation type and its constructor/read function.

## Important APIs and Types
Defines `OSTREE_TYPE_BLOB_READER_BASE64` and declares final type `OstreeBlobReaderBase64` deriving from `GDataInputStream`. Exports `_ostree_blob_reader_base64_new()` and `ostree_blob_reader_base64_read_blob()`.

## Control Flow
No runtime control flow is present. The header provides type metadata and function prototypes used by the implementation and callers.

## State and Persistence
The type's state is inherited stream state; the header does not define additional fields.

## Dependencies and Integration Points
Includes `ostree-blob-reader.h`, so users can treat the type as an `OstreeBlobReader`. `_OSTREE_PUBLIC` annotations expose the symbols according to libostree's internal/public visibility rules.

## Risks
The leading underscore constructor suggests internal API despite public visibility annotations. Callers must preserve the `GInputStream` lifetime through the object construction contract rather than retaining raw pointers.

## Test Signals
Compile-time type checks, interface casts, and construction through the declared constructor are sufficient for the header; behavioral tests belong to the `.c` file.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-base64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-pem.c -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader-pem.c

## Purpose
Implements a simple RFC 7468 PEM reader that extracts base64 payloads from `-----BEGIN LABEL-----` / `-----END LABEL-----` blocks and optionally filters by an expected label.

## Important APIs and Types
`OstreeBlobReaderPem` is a final `GDataInputStream` subclass implementing `OstreeBlobReader`. It has construct-only string property `label`. `_ostree_blob_reader_pem_new()` creates the reader. `_ostree_read_pem_block()` is a reusable parser returning the next decoded block and optional label. `ostree_blob_reader_pem_read_blob()` enforces the instance label.

## Control Flow
The parser alternates between `PEM_INPUT_STATE_OUTER` and `PEM_INPUT_STATE_INNER`. It strips input lines, ignores blanks, searches for a begin marker, accumulates inner base64 lines, validates the end marker label with `strncmp()`, decodes the accumulated buffer in place, zeroes trailing encoded bytes, and returns the payload. EOF inside a block raises `PEM trailer not found`; a mismatched trailer raises `Unmatched PEM header`; a label mismatch raises `Unexpected label`.

## State and Persistence
Reader state consists of the expected label and the base stream cursor. Each read consumes through exactly one matching block or an error/EOF. Payloads are returned as detached `GBytes`.

## Dependencies and Integration Points
Depends on `ostree-blob-reader-pem.h`, `ostree-blob-reader-private.h`, GLib base64/string APIs, and the `OstreeBlobReader` interface. It is suitable for PEM encoded signatures, certificates, or keys where libostree wants no legacy PEM headers.

## Risks
The label comparison checks only `end - start` bytes and does not independently verify equal label length, so prefixes deserve tests. The parser deliberately does not support RFC 1421 headers and treats any non-END inner line as base64 data. Decoding large PEM payloads accumulates the full encoded body in memory.

## Test Signals
Tests should cover multiple blocks, blank lines, label filtering, mismatched labels, missing trailer, payload decoding, EOF behavior, and malformed or header-bearing PEM inputs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-pem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-pem.h -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader-pem.h

## Purpose
Declares the PEM blob reader implementation type and public helper functions for PEM block reading.

## Important APIs and Types
Defines `OSTREE_TYPE_BLOB_READER_PEM` and declares final type `OstreeBlobReaderPem` deriving from `GDataInputStream`. Exposes `_ostree_blob_reader_pem_new()`, `_ostree_read_pem_block()`, and `ostree_blob_reader_pem_read_blob()`.

## Control Flow
The header has no runtime flow. It establishes the constructor and parsing APIs used by PEM reader consumers and by the implementation.

## State and Persistence
State is implementation-private: expected label plus underlying stream position.

## Dependencies and Integration Points
Includes `ostree-blob-reader.h` so the type can be consumed through the shared blob-reader abstraction. `_ostree_read_pem_block()` accepts a `GDataInputStream`, making the parser reusable outside the object wrapper.

## Risks
The helper returns nullable `GBytes` for both EOF and error, so callers must observe `GError`. The label out parameter transfers ownership when requested.

## Test Signals
Header-level signals are compile and introspection checks for type declaration, constructor linkage, and interface compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-pem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader-private.h

## Purpose
Aggregates the private blob reader implementations into one internal include.

## Important APIs and Types
It includes `ostree-blob-reader-base64.h`, `ostree-blob-reader-pem.h`, and `ostree-blob-reader-raw.h`, making the concrete constructors and read functions available to internal libostree code.

## Control Flow
No runtime logic is present.

## State and Persistence
No state is stored.

## Dependencies and Integration Points
This is an integration header for modules that need access to all blob reader variants without including each concrete header manually.

## Risks
Because it exposes concrete internal readers together, adding a new reader here can widen internal compile dependencies. It should remain private to avoid making internal constructors a stable external contract.

## Test Signals
Compile coverage of internal users is sufficient; missing includes would surface as unknown type or prototype failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-raw.c -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader-raw.c

## Purpose
Implements `OstreeBlobReaderRaw`, a line-oriented raw blob reader that returns each input line as bytes without decoding.

## Important APIs and Types
`_ostree_blob_reader_raw_new()` constructs the `GDataInputStream` subclass. `ostree_blob_reader_raw_read_blob()` implements `OstreeBlobReaderInterface.read_blob`.

## Control Flow
The read method calls `g_data_input_stream_read_line()`, propagates any local read error, returns `NULL` on EOF, and otherwise wraps the line buffer with `g_bytes_new_take()` using the line length returned by GIO.

## State and Persistence
The reader persists only the underlying stream cursor. Each successful call consumes one line and returns an owned immutable byte blob.

## Dependencies and Integration Points
Depends on `ostree-blob-reader-raw.h`, `GDataInputStream`, and the shared blob reader interface. It is used wherever libostree needs newline-delimited opaque blobs.

## Risks
Newline terminators are not included in returned data because `g_data_input_stream_read_line()` strips them. This reader is unsuitable for blobs that may contain embedded newlines or require exact original line endings.

## Test Signals
Tests should cover multi-line input, EOF, empty lines, cancellation/read errors, and exact returned byte lengths.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-raw.h -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader-raw.h

## Purpose
Declares the raw line blob reader type.

## Important APIs and Types
Defines `OSTREE_TYPE_BLOB_READER_RAW` and final type `OstreeBlobReaderRaw` deriving from `GDataInputStream`. Exposes `_ostree_blob_reader_raw_new()` and `ostree_blob_reader_raw_read_blob()`.

## Control Flow
No runtime flow; this header provides type and function declarations.

## State and Persistence
State is inherited stream position only.

## Dependencies and Integration Points
Includes `ostree-blob-reader.h` and participates in the shared blob reader interface family.

## Risks
As with the other concrete reader headers, symbol visibility and underscore naming indicate internal use; external callers should prefer the common interface when possible.

## Test Signals
Compile/type registration checks plus `.c` behavioral tests validate this declaration.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader-raw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader.c -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader.c

## Purpose
Defines the `OstreeBlobReader` GObject interface and the common dispatch function for reading blobs.

## Important APIs and Types
`G_DEFINE_INTERFACE()` registers the interface. `ostree_blob_reader_read_blob()` asserts the instance implements `OSTREE_TYPE_BLOB_READER` and calls the implementation's `read_blob` vfunc.

## Control Flow
Initialization only logs a debug message. Runtime dispatch is one virtual call through `OSTREE_BLOB_READER_GET_IFACE(self)->read_blob`.

## State and Persistence
The interface owns no state. Concrete implementations define stream cursor and decoding state.

## Dependencies and Integration Points
Depends on `ostree-blob-reader.h` and GObject. It integrates raw, base64, and PEM readers under a single nullable `GBytes` read contract.

## Risks
The interface does not provide a default `read_blob`; a class that fails to set the vfunc will crash when dispatched. Callers must use the `GError` convention to distinguish EOF from failure.

## Test Signals
Interface conformance tests should instantiate each concrete reader through the interface and validate EOF/error behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader.h -->
# sources/cloud-native/ostree/src/libostree/ostree-blob-reader.h

## Purpose
Declares the `OstreeBlobReader` interface used by line/block-oriented blob decoders.

## Important APIs and Types
Defines `OSTREE_TYPE_BLOB_READER`, declares `G_DECLARE_INTERFACE`, and defines `OstreeBlobReaderInterface` with one vfunc: `GBytes *(*read_blob)(OstreeBlobReader*, GCancellable*, GError**)`. Exposes `ostree_blob_reader_read_blob()`.

## Control Flow
The header defines the dispatch contract but no implementation flow.

## State and Persistence
No state is defined at interface level. Implementations are free to maintain parser or stream state.

## Dependencies and Integration Points
Includes `ostree-types.h` and `<gio/gio.h>`. Concrete readers implement this interface and callers can consume all formats through a single API.

## Risks
The nullable return conflates EOF and error unless `GError` is checked. The interface is synchronous and reads one complete blob per call, so large blob formats can imply whole-blob buffering.

## Test Signals
ABI/type checks, vfunc dispatch tests, and concrete implementation coverage validate the interface contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-blob-reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bloom-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bloom-private.h

## Purpose
Declares libostree's internal Bloom filter API for building, sealing, loading, and querying compact membership filters.

## Important APIs and Types
Defines opaque `OstreeBloom` and `OstreeBloomHashFunc(element, k)`. Declares constructors `ostree_bloom_new()` and `ostree_bloom_new_from_bytes()`, ref management, `ostree_bloom_add_element()`, `ostree_bloom_seal()`, `ostree_bloom_maybe_contains()`, getters for size/k/hash function, and `ostree_str_bloom_hash()`.

## Control Flow
No control flow exists in the header. The API shape enforces a mutable-build then immutable-query lifecycle.

## State and Persistence
The serialized persistent state is only the bit array returned by `ostree_bloom_seal()`. Callers must persist the hash function identity and `k` separately.

## Dependencies and Integration Points
Depends on GLib/GObject/GIO and libglnx. It declares a boxed type and autoptr cleanup, so internal users can store filters as boxed values or stack-managed pointers.

## Risks
This is marked internal and unstable. Loading bytes with the wrong `k` or hash function silently changes membership semantics. Bloom filters are probabilistic: false positives are expected, false negatives indicate bugs or parameter mismatch.

## Test Signals
Tests should verify add/query behavior, serialized byte stability, getter consistency, false-negative absence, and string hash determinism.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bloom-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bloom.c -->
# sources/cloud-native/ostree/src/libostree/ostree-bloom.c

## Purpose
Implements an internal Bloom filter with stable serialized bit-array output and a SipHash-based string hash helper.

## Important APIs and Types
`struct _OstreeBloom` stores `ref_count`, `n_bytes`, mutability, either owned mutable bytes or immutable `GBytes`, `k`, and `hash_func`. Public-internal functions create mutable filters, load immutable filters from `GBytes`, ref/unref, add elements, query possible membership, seal to `GBytes`, return configuration, and hash strings through `ostree_str_bloom_hash()`.

## Control Flow
Creation validates size, `k`, and hash function. `ostree_bloom_add_element()` runs the hash function for `i=0..k-1`, modulo-maps each hash into `n_bytes * 8`, and sets bits. `ostree_bloom_maybe_contains()` repeats the hashes and returns false on the first missing bit. `ostree_bloom_seal()` converts mutable bytes into immutable `GBytes` and can be called repeatedly. `ostree_str_bloom_hash()` fills a 16-byte SipHash key with the `k` value and hashes the input string.

## State and Persistence
Before sealing, the bit array is mutable and owned as `guint8*`. After sealing or loading, state is immutable `GBytes`. The serialized format is the raw bit array only, so metadata must travel alongside it.

## Dependencies and Integration Points
Depends on GLib boxed types, `GBytes`, assertions, endian helpers, and the embedded SipHash implementation. It is suitable for repository metadata acceleration where compact approximate membership matters.

## Risks
`ostree_bloom_ref()` contains a notable guard requiring `ref_count == G_MAXUINT - 1`; that appears inverted for normal reference increments and should be covered by tests. The implementation is not thread-safe around mutable state or manual ref_count. False-positive rates depend entirely on caller-chosen size and `k`.

## Test Signals
Signals include ref/unref lifecycle tests, add/seal/query tests, load-from-bytes parity, deterministic serialized bytes, string hash test vectors, NULL validation behavior, and regression coverage for the `ostree_bloom_ref()` guard.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bloom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser-private.h

## Purpose
Declares private helpers for retrieving bootconfig parser internals not exposed in the public header.

## Important APIs and Types
`_ostree_bootconfig_parser_filename()` returns the parsed basename. `_ostree_bootconfig_parser_get_extra_keys_variant()` returns non-standard bootloader keys as a `GVariant` dictionary.

## Control Flow
No runtime flow is present in the header.

## State and Persistence
The helpers expose already parsed in-memory parser state. Extra keys can be serialized by deployment code to preserve consumer extensions.

## Dependencies and Integration Points
Includes `ostree-bootconfig-parser.h`. Used by sysroot/deployment internals that need filename metadata or extension-key preservation during staged deployment serialization.

## Risks
The filename pointer is transfer-none and tied to parser lifetime. The extra-key filter must stay synchronized with standard BLS keys in the implementation.

## Test Signals
Tests should parse files with custom keys, call the private variant helper through internal code, and confirm standard keys are excluded while extension keys survive round trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser.c -->
# sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser.c

## Purpose
Implements `OstreeBootconfigParser`, a GObject for parsing, mutating, cloning, and writing Boot Loader Specification style entry files while preserving OSTree-specific boot metadata such as retry counters and overlay initrds.

## Important APIs and Types
The object stores `filename`, separator characters, `tries_left`, `tries_done`, a string-to-string `options` hash table, and `overlay_initrds`. Public APIs include `new`, `clone`, `parse`, `parse_at`, `write`, `write_at`, `set`, `get`, overlay initrd setters/getters, and boot try getters. Private APIs expose the filename and non-standard key variant.

## Control Flow
Parsing reads the file as UTF-8, splits on newlines, accepts lines beginning with an ASCII alpha character, splits each accepted line on space or tab into key/value, stores the first `initrd` in `options`, stores additional `initrd` lines as overlays, parses `+LEFT-DONE` retry counters from the basename, and records the basename. Writing emits standard BLS keys in deterministic order, then overlay initrds, then unknown keys. Clone duplicates options, filename, and overlay initrds.

## State and Persistence
State is in-memory until `write_at()` atomically replaces the target file with `glnx_file_replace_contents_at()`. Unknown/extension keys are preserved in memory and can be serialized through `_ostree_bootconfig_parser_get_extra_keys_variant()`.

## Dependencies and Integration Points
Depends on GLib/GObject, libglnx file helpers, `otutil.h`, and BLS semantics. Bootloader backends read parsed configs from sysroot and use keys such as `title`, `version`, `linux`, `initrd`, `options`, `devicetree`, `fdtdir`, `aboot`, and `abootcfg`.

## Risks
Parser accepts only alpha-starting lines and ignores comments or malformed lines silently. Hash-table iteration makes unknown-key write order nondeterministic. `parse_bootloader_tries()` does not require the counter suffix to end cleanly before extension text. Overlay initrd setting asserts the primary `initrd` already exists.

## Test Signals
Tests should cover standard BLS parse/write, duplicate initrd handling, extension-key preservation, try-counter filenames, malformed lines, deterministic standard key ordering, and staged deployment round trips with custom keys.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser.h

## Purpose
Declares the public `OstreeBootconfigParser` GObject API.

## Important APIs and Types
Defines `OSTREE_TYPE_BOOTCONFIG_PARSER`, cast/check macros, opaque `OstreeBootconfigParser`, type getter, constructor, clone, parse/write APIs for `GFile` and fd-relative paths, key setters/getters, overlay initrd setters/getters, and boot try getters.

## Control Flow
No implementation flow; the header defines callable API and ownership conventions.

## State and Persistence
The parser owns bootconfig key/value state and writes it back to files through the implementation.

## Dependencies and Integration Points
Includes `<gio/gio.h>` and is consumed by sysroot deployment code plus bootloader backends.

## Risks
Callers receive transfer-none strings and string vectors from getters. Because parsing is single-use on a fresh parser in the implementation, callers should not reparse into an initialized instance.

## Test Signals
ABI compilation, GObject type checks, introspection expectations, and behavior tests for the implementation validate this header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-aboot.c -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-aboot.c

## Purpose
Implements the Android-style `aboot` bootloader backend. It does not auto-detect active installations; when selected, it writes a stamp and later runs `aboot-deploy` after BLS configs are synchronized.

## Important APIs and Types
`OstreeBootloaderAboot` stores an `OstreeSysroot*`. Interface methods are query, get name, write config, and post-BLS sync. `_ostree_aboot_get_bls_config()` extracts `aboot`, `abootcfg`, `version`, `linux`, `initrd`, and `options` from the first BLS config.

## Control Flow
`query()` always reports inactive. `write_config()` creates `boot/ostree-bootloader-update.stamp`. `post_bls_sync()` returns immediately if the stamp is absent, otherwise reads the first BLS config, builds `/boot`-prefixed kernel/initrd paths, spawns `aboot-deploy -r . -c <abootcfg> -o <options> <aboot>` after `fchdir()` into the sysroot fd, checks exit status, and removes the stamp.

## State and Persistence
The stamp file is persistent state indicating deferred bootloader execution. The backend reads BLS files from the target bootversion and mutates host bootloader state through the external `aboot-deploy` command.

## Dependencies and Integration Points
Depends on sysroot private APIs, deployment/private headers, libarchive private headers, libglnx, and the generic `OstreeBootloader` interface. It integrates with finalization code that calls post-BLS sync after config generation.

## Risks
The backend assumes required custom BLS keys exist and uses only the first config. It does not chroot, so command behavior depends on `fchdir` and host environment. Query returning inactive means selection must be explicit.

## Test Signals
Tests should simulate stamp presence/absence, missing BLS keys, command failure, successful stamp removal, and explicit backend selection rather than auto-detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-aboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-aboot.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-aboot.h

## Purpose
Declares the `OstreeBootloaderAboot` backend type.

## Important APIs and Types
Defines type/cast/check macros, opaque `OstreeBootloaderAboot`, type getter, and `_ostree_bootloader_aboot_new(OstreeSysroot*)`.

## Control Flow
No runtime flow; declarations only.

## State and Persistence
The implementation stores a referenced sysroot and uses a stamp file for deferred work.

## Dependencies and Integration Points
Includes `ostree-bootloader.h`, binding this backend to the shared bootloader interface.

## Risks
The constructor is internal and requires a valid loaded sysroot. Consumers should call through the interface after construction.

## Test Signals
Compile/type registration and construction tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-aboot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-grub2.c -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-grub2.c

## Purpose
Implements the GRUB2 bootloader backend, including active installation detection, GRUB config generation, execution of either system `grub2-mkconfig` or the builtin generator, and special EFI replacement handling.

## Important APIs and Types
`OstreeBootloaderGrub2` stores sysroot, BIOS config paths, EFI config path, and `is_efi`. Key functions are `_ostree_bootloader_grub2_query()`, `_ostree_bootloader_grub2_generate_config()`, `_ostree_bootloader_grub2_write_config()`, and `_ostree_bootloader_grub2_is_atomic()`. `Grub2ChildSetupData` passes bootversion, EFI state, and optional chroot root into the child setup.

## Control Flow
Query first checks bootupd state and disables itself for static bootupd configs, then detects BIOS configs under `boot/grub/grub.cfg` or `boot/grub2/grub.cfg`, then scans `boot/efi/EFI/*/grub.cfg` excluding `BOOT`. Config generation reads BLS entries, emits `menuentry` blocks, hardcoded video/gzio/root-cache setup, `linux*`, `initrd*`, and optional `devicetree` commands. Write config chooses system or builtin generator from build flags/env, optionally chroots into the first deployment when running from an installer, writes a temporary config, fdatasyncs it, and for EFI copies old config aside then renames the new file into place.

## State and Persistence
Persistent state is the generated `grub.cfg` under either bootversion-specific loader paths or EFI vendor directories. EFI replacement is explicitly non-atomic due to FAT limitations; BIOS writes use bootversion paths.

## Dependencies and Integration Points
Depends on sysroot private BLS reading, GIO file APIs, Unix output streams, mount namespace/chroot syscalls, `grub2-mkconfig`, `ostree-grub-generator`, bootupd state, and environment variables such as `OSTREE_GRUB2_EXEC`, `GRUB2_BOOT_DEVICE_ID`, and `GRUB2_PREPARE_ROOT_CACHE`.

## Risks
The bootupd check is a string search rather than JSON parsing. EFI updates are non-atomic and depend on copy/rename behavior on FAT. Child setup uses mount namespace and chroot operations that can fail in constrained environments. Missing `linux` keys or absent generator environment variables are hard failures.

## Test Signals
Tests should cover BIOS/EFI detection, bootupd static-config exclusion, builtin vs system generator selection, BLS-to-menuentry rendering, chroot setup path selection, command failure propagation, fdatasync errors, and EFI old/new replacement behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-grub2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-grub2.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-grub2.h

## Purpose
Declares the GRUB2 bootloader backend and its config-generation helper.

## Important APIs and Types
Defines `OSTREE_TYPE_BOOTLOADER_GRUB2`, cast/check macros, opaque `OstreeBootloaderGrub2`, type getter, `_ostree_bootloader_grub2_new()`, and `_ostree_bootloader_grub2_generate_config()`.

## Control Flow
No implementation flow; the header exposes the constructor and generator entry point used by private command glue.

## State and Persistence
The backend implementation owns sysroot and detected config path state. The generator writes GRUB text to a supplied target fd.

## Dependencies and Integration Points
Includes `ostree-bootloader.h`. `_ostree_bootloader_grub2_generate_config()` is exported internally through `ostree_cmd__private__()` for the command-side generator.

## Risks
Callers of the generator must provide the environment expected by the implementation. The backend should be consumed through the shared interface except for the generator hook.

## Test Signals
Compile/link coverage and generator invocation through the private vtable validate this header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-grub2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-syslinux.c -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-syslinux.c

## Purpose
Implements the syslinux bootloader backend by preserving non-OSTree labels and regenerating OSTree labels from BLS entries.

## Important APIs and Types
`OstreeBootloaderSyslinux` stores an `OstreeSysroot*`. The backend queries `boot/syslinux/syslinux.cfg`, writes `boot/loader.<bootversion>/syslinux.cfg`, and uses `append_config_from_loader_entries()` to render BLS entries into syslinux directives.

## Control Flow
Query checks for the syslinux config path with `fstatat`. Write reads current config through the boot loader symlink, splits lines, tracks `LABEL` blocks, preserves non-OSTree labels based on their `KERNEL` path, drops OSTree labels for regeneration, handles `DEFAULT` regeneration when it points to OSTree or is absent, appends entries from BLS configs, joins lines, and replaces the new bootversion config with datasync.

## State and Persistence
Persistent output is the bootversion-specific syslinux config. Existing non-OSTree boot entries are preserved, while OSTree-managed entries are derived from current BLS state.

## Dependencies and Integration Points
Depends on sysroot private BLS reading, repo private `enable_bootprefix`, libglnx file helpers, and `OstreeBootconfigParser` keys `title`, `linux`, `initrd`, `devicetree`, and `options`.

## Risks
Detection of OSTree labels depends on kernel paths starting with `/ostree/` or `/boot/ostree/` and title patterns for defaults. Missing `KERNEL` after a label or missing `linux` in BLS fails the write. Formatting assumes tab-indented syslinux label blocks.

## Test Signals
Tests should cover preserving non-OSTree labels, regenerating defaults, bootprefix on/off, missing `linux`, labels without `KERNEL`, and output line ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-syslinux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-syslinux.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-syslinux.h

## Purpose
Declares the syslinux bootloader backend type.

## Important APIs and Types
Defines type/cast/check macros, opaque `OstreeBootloaderSyslinux`, type getter, and `_ostree_bootloader_syslinux_new()`.

## Control Flow
No runtime control flow in the header.

## State and Persistence
Implementation state is a referenced sysroot; persistent state is generated syslinux config.

## Dependencies and Integration Points
Includes `ostree-bootloader.h` and participates in the generic bootloader interface.

## Risks
Constructor is internal and assumes sysroot state is initialized enough for query/write.

## Test Signals
Type registration and constructor tests validate the declaration.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-syslinux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-uboot.c -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-uboot.c

## Purpose
Implements the U-Boot backend by generating `uEnv.txt` variables from BLS entries and optionally appending deployment-provided U-Boot environment snippets.

## Important APIs and Types
`OstreeBootloaderUboot` stores an `OstreeSysroot*`. It queries `boot/loader/uEnv.txt`, writes `boot/loader.<bootversion>/uEnv.txt`, uses `create_config_from_boot_loader_entries()` for variable generation, and `append_system_uenv()` to read `$deployment/usr/lib/ostree-boot/uEnv.txt` based on the `ostree=` kernel argument.

## Control Flow
Query checks the active uEnv path. Write reads the existing config to ensure the path exists, builds new lines from BLS configs, suffixes variables for entries after the first, emits `kernel_image`, `ramdisk_image`, `fdt_file`, `fdtdir`, and `bootargs`, appends system uEnv for the first deployment if present, joins lines, and datasync-replaces the bootversion config.

## State and Persistence
Persistent state is the generated bootversion-specific `uEnv.txt`. The backend also reads optional deployment-owned environment content without modifying it.

## Dependencies and Integration Points
Depends on sysroot private BLS reading, kernel argument parsing, libglnx fd-relative reads, and `OstreeBootconfigParser` keys `linux`, `initrd`, `devicetree`, `fdtdir`, and `options`.

## Risks
`append_system_uenv()` requires an `ostree=` kernel argument and skips the leading character before constructing the deployment path, so malformed kargs fail writes. Existing config contents are read but not preserved. Missing BLS `linux` is fatal.

## Test Signals
Tests should cover variable suffix generation for multiple deployments, optional initrd/devicetree/fdtdir, appending deployment uEnv, missing `ostree=` argument, and missing existing `uEnv.txt`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-uboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-uboot.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-uboot.h

## Purpose
Declares the U-Boot bootloader backend type.

## Important APIs and Types
Defines type/cast/check macros, opaque `OstreeBootloaderUboot`, type getter, and `_ostree_bootloader_uboot_new()`.

## Control Flow
No runtime flow; declarations only.

## State and Persistence
The implementation keeps a sysroot reference and writes bootversion-specific uEnv files.

## Dependencies and Integration Points
Includes `ostree-bootloader.h` for shared interface integration.

## Risks
Internal constructor should only be used by sysroot bootloader selection code.

## Test Signals
Compile/type checks and constructor coverage are sufficient for the header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-uboot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-zipl.c -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-zipl.c

## Purpose
Implements the IBM Z `zipl` bootloader backend, including deferred zipl execution, secure boot detection, and Secure Execution image generation on s390x.

## Important APIs and Types
`OstreeBootloaderZipl` stores an `OstreeSysroot*`. The backend query is architecture-dependent, write creates `boot/ostree-bootloader-update.stamp`, and post-BLS sync invokes either Secure Execution handling or standard `zipl`. Secure Execution helpers mount `/dev/disk/by-label/se`, find host keys, copy/augment initrd with LUKS material through libarchive, run `genprotimg`, and call `zipl` on the generated secure image.

## Control Flow
Query returns active on `__s390x__` only. Post-sync skips unprivileged contexts and no-stamp cases, chooses a target deployment for containerized execution when not booted, checks Secure Execution sysfs, runs the SE flow if enabled, otherwise detects Secure Boot through sysfs or `/dev/kmsg`, runs `zipl --secure 1|auto -V` either in the deployment via bubblewrap helper or directly, checks exit status, and removes the stamp.

## State and Persistence
Persistent state includes the update stamp, generated secure boot image under `/sysroot/se/sdboot`, and external bootloader state written by `zipl`. The Secure Execution path temporarily mounts and unmounts the SE partition and writes anonymous temporary initrd/cmdline files.

## Dependencies and Integration Points
Depends on sysroot/deployment private APIs, libarchive on s390x, GIO Unix input streams, sysfs, `/dev/kmsg`, `genprotimg`, `zipl`, host key files, LUKS key/config paths, and the shared bootloader interface.

## Risks
The SE enable path chains operations with `&&`; if an intermediate step fails after mount, unmount may be skipped. Reading `/dev/kmsg` assumes lines are available and does not visibly handle NULL lines before `strstr`. The backend touches sensitive LUKS material and depends on privileged host execution.

## Test Signals
Tests should cover stamp lifecycle, unprivileged no-op, s390x vs non-s390x query, Secure Boot sysfs and kmsg fallbacks, SE key discovery, missing LUKS material, `genprotimg`/`zipl` failures, and deployment-contained execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-zipl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-zipl.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-zipl.h

## Purpose
Declares the zIPL bootloader backend type.

## Important APIs and Types
Defines type/cast/check macros, opaque `OstreeBootloaderZipl`, type getter, and `_ostree_bootloader_zipl_new()`.

## Control Flow
No runtime flow in the header.

## State and Persistence
Implementation state is a sysroot reference; persistent backend state is the zipl update stamp and external zipl-installed boot state.

## Dependencies and Integration Points
Includes `ostree-bootloader.h` and integrates with the generic bootloader interface.

## Risks
Internal constructor should only be used in bootloader selection with an initialized sysroot.

## Test Signals
Type registration, constructor coverage, and interface cast checks validate the declaration.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-zipl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader.c -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader.c

## Purpose
Defines the shared `OstreeBootloader` interface dispatch layer used by sysroot deployment code to operate on concrete bootloader backends uniformly.

## Important APIs and Types
`G_DEFINE_INTERFACE()` registers `OstreeBootloader`. Dispatch helpers are `_ostree_bootloader_query()`, `_ostree_bootloader_get_name()`, `_ostree_bootloader_write_config()`, `_ostree_bootloader_post_bls_sync()`, and `_ostree_bootloader_is_atomic()`.

## Control Flow
Each helper asserts the instance implements the interface and forwards to the relevant vfunc. `post_bls_sync` defaults to success if the backend omits the hook. `is_atomic` defaults to true if the backend omits the hook.

## State and Persistence
The interface layer stores no state. Concrete implementations own sysroot references and persistent bootloader files/stamps.

## Dependencies and Integration Points
Depends on `ostree-bootloader.h` and GObject. It is the integration point between sysroot deployment orchestration and GRUB2, syslinux, U-Boot, zIPL, aboot, and other backends.

## Risks
Backends must implement mandatory `query`, `get_name`, and `write_config` vfuncs. The default atomic=true can be wrong for a backend that forgets to override non-atomic behavior.

## Test Signals
Interface dispatch tests should verify each backend's name/query/write path and default handling for optional hooks.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader.h

## Purpose
Declares the internal bootloader interface contract.

## Important APIs and Types
Defines `OstreeBootloaderInterface` with vfuncs `query`, `get_name`, `write_config`, optional `post_bls_sync`, and optional `is_atomic`. Declares type/cast macros, autoptr cleanup, type getter, and dispatch helpers.

## Control Flow
No implementation flow in the header; it defines the backend contract.

## State and Persistence
State is backend-specific. The interface methods operate over bootversion, deployment arrays, cancellables, and errors.

## Dependencies and Integration Points
Includes `<ostree.h>` and `otutil.h`. Concrete bootloader headers include this file and sysroot deployment code calls the dispatch helpers.

## Risks
`write_config` receives `GPtrArray *new_deployments`; backend assumptions about length and ordering must match sysroot deployment orchestration. Atomicity reporting is critical for safe bootversion switching.

## Test Signals
Compile/type checks, backend interface conformance, and orchestration tests that call through dispatch helpers validate this header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-chain-input-stream.c -->
# sources/cloud-native/ostree/src/libostree/ostree-chain-input-stream.c

## Purpose
Implements `OstreeChainInputStream`, a `GInputStream` that presents a sequence of child input streams as one contiguous stream.

## Important APIs and Types
Private state stores a referenced `GPtrArray *streams` and current `index`. `ostree_chain_input_stream_new()` constructs the stream with construct-only pointer property `streams`. The class overrides `read_fn` and `close_fn`.

## Control Flow
Read checks cancellation, returns EOF if all children are consumed, otherwise reads from the current child. If a child returns EOF, it advances to the next child and retries until data or total EOF. Close iterates all children and closes each, stopping on the first close error.

## State and Persistence
State is transient read position across child streams. It does not persist data; it composes existing streams.

## Dependencies and Integration Points
Depends on GLib/GIO. `ostree-core.c` uses it to combine length-prefixed file metadata headers with optional content streams for OSTree object serialization.

## Risks
The constructor stores a referenced `GPtrArray`, but child stream ownership depends on the array's free function. Close stops at first failure, potentially leaving later children open. Zero-byte reads from unusual child streams are treated as EOF.

## Test Signals
Tests should cover multiple streams, empty child streams, cancellation, close propagation, read boundaries across children, and ownership/ref behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-chain-input-stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-chain-input-stream.h -->
# sources/cloud-native/ostree/src/libostree/ostree-chain-input-stream.h

## Purpose
Declares the chain input stream type, hidden from GI scanner.

## Important APIs and Types
Defines GObject type/cast/check macros, `OstreeChainInputStream`, class struct with reserved padding, type getter, and `ostree_chain_input_stream_new(GPtrArray *streams)`.

## Control Flow
No runtime flow in the header.

## State and Persistence
Implementation-private state tracks stream array and current index.

## Dependencies and Integration Points
Includes `<ostree.h>` and is used by core object stream construction.

## Risks
The `streams` constructor argument is a raw `GPtrArray*`; callers must supply an array whose child lifetime semantics are correct.

## Test Signals
Compile/type checks and implementation behavior tests validate the header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-chain-input-stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-checksum-input-stream.c -->
# sources/cloud-native/ostree/src/libostree/ostree-checksum-input-stream.c

## Purpose
Implements `OstreeChecksumInputStream`, a `GFilterInputStream` that updates a caller-owned `GChecksum` with bytes successfully read from the base stream.

## Important APIs and Types
Private state stores `GChecksum *checksum`. `ostree_checksum_input_stream_new()` constructs the filter with `base-stream` and construct-only pointer property `checksum`. The class overrides `read_fn`.

## Control Flow
Read checks cancellation, delegates to the base stream, and calls `g_checksum_update()` only when the delegated read returns a positive byte count. EOF and errors do not update the checksum.

## State and Persistence
The stream does not own or free the checksum; it mutates caller-owned checksum state as reads progress. The only stream state comes from the base `GFilterInputStream`.

## Dependencies and Integration Points
Depends on GLib/GIO checksum and stream APIs. It integrates with code that needs streaming hashing without manually wrapping each read call.

## Risks
The checksum pointer is borrowed; callers must keep it alive longer than the stream. Partial reads update incrementally, so abandoning the stream yields a partial checksum by design.

## Test Signals
Tests should compare checksum results against hashing the full input, cover partial reads, EOF, cancellation, read errors, and lifetime expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-checksum-input-stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-checksum-input-stream.h -->
# sources/cloud-native/ostree/src/libostree/ostree-checksum-input-stream.h

## Purpose
Declares the checksum-updating filter input stream type.

## Important APIs and Types
Defines type/cast/check macros, `OstreeChecksumInputStream`, class struct with reserved padding, type getter, and `ostree_checksum_input_stream_new(GInputStream*, GChecksum*)`.

## Control Flow
No implementation flow in the header.

## State and Persistence
Implementation-private state stores a borrowed `GChecksum*`.

## Dependencies and Integration Points
Includes `<gio/gio.h>` and supports stream hashing integrations.

## Risks
The borrowed checksum lifetime is not visible from the type system. Callers need to manage it explicitly.

## Test Signals
Compile/type checks and read-path checksum tests validate the declaration.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-checksum-input-stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-cmd-private.c -->
# sources/cloud-native/ostree/src/libostree/ostree-cmd-private.c

## Purpose
Exports a private vtable used to share selected libostree internals with the OSTree command-line binary without making their headers public API.

## Important APIs and Types
`ostree_cmd__private__()` returns a static `OstreeCmdPrivateVTable`. It maps command-side hooks to `_ostree_impl_system_generator`, a local wrapper around `_ostree_bootloader_grub2_generate_config()`, static delta dump/query/delete helpers, repo binding verification, sysroot staged finalization, boot-complete handling, and soft reboot preparation.

## Control Flow
The function initializes a static table literal and returns its address. The only wrapper delegates GRUB2 generation to the bootloader implementation.

## State and Persistence
The static vtable is process-lifetime immutable state. Called functions perform the actual repository, sysroot, bootloader, or static-delta mutations.

## Dependencies and Integration Points
Depends on private headers for GRUB2, core, repo, static deltas, sysroot, and command declarations. It is a bridge between libostree and command code while preserving a narrow exported symbol.

## Risks
The symbol is exported but intentionally not public API; vtable layout changes require command/library version alignment. A stale command binary could call mismatched function slots.

## Test Signals
Tests should verify CLI operations that use each vtable slot, especially GRUB generation, static delta commands, staged finalization, and boot-complete paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-cmd-private.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-cmd-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-cmd-private.h

## Purpose
Declares the private command vtable contract exported from libostree to OSTree command-line code.

## Important APIs and Types
Declares `_ostree_impl_system_generator()` and `OstreeCmdPrivateVTable`, whose function pointers cover systemd generator output, GRUB2 config generation, static delta operations, repo binding verification, staged finalization, boot complete, and soft reboot preparation. Declares `_OSTREE_PUBLIC const OstreeCmdPrivateVTable *ostree_cmd__private__(void)`.

## Control Flow
No implementation flow; this file defines ABI shape for the private bridge.

## State and Persistence
No state directly. Function pointers may trigger persistent repo/sysroot/bootloader changes when invoked.

## Dependencies and Integration Points
Includes `ostree-types.h`. The command binary uses this header while regular external consumers should not.

## Risks
Although private, the exported symbol and struct layout are ABI-sensitive for the matching command binary. Adding/reordering fields can break mixed-version execution.

## Test Signals
Build/link tests for the command binary and integration coverage for each vtable function are the key signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-cmd-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-content-writer.c -->
# sources/cloud-native/ostree/src/libostree/ostree-content-writer.c

## Purpose
Implements `OstreeContentWriter`, a `GOutputStream` wrapper for writing bare repository content and finalizing it to an OSTree checksum.

## Important APIs and Types
`OstreeContentWriter` stores a referenced `OstreeRepo` and `OstreeRepoBareContent output`. `_ostree_content_writer_new()` opens the bare content destination with expected checksum, metadata, and length. The stream overrides write and close. `ostree_content_writer_finish()` commits the content and returns the actual checksum string.

## Control Flow
Construction initializes repo bare content output. Writes check cancellation and pass buffers to `_ostree_repo_bare_content_write()`, returning the requested count on success. Close intentionally does nothing because callers are expected to call finish. Finalize cleans up repo reference and any unfinished bare content state. Finish commits with `_ostree_repo_bare_content_commit()` and returns a duplicated checksum.

## State and Persistence
Persistent state is the repository object being written through the bare content helper. Until finish commits, output may be temporary/cleanup-managed. Finalize cleans up uncommitted state.

## Dependencies and Integration Points
Depends on autocleanup declarations, `ostree-content-writer.h`, and repo private bare-content APIs. It integrates stream-writing callers with repository object storage.

## Risks
Calling `g_output_stream_close()` is not enough to commit; callers must call `ostree_content_writer_finish()`. The writer returns `count` if the private write helper succeeds, so partial write semantics are hidden inside that helper.

## Test Signals
Tests should cover successful write/finish checksum, cancellation, commit failure, finalize cleanup without finish, metadata propagation, and incorrect expected checksum behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-content-writer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-content-writer.h -->
# sources/cloud-native/ostree/src/libostree/ostree-content-writer.h

## Purpose
Declares the content writer stream type and finish API.

## Important APIs and Types
Defines `OSTREE_TYPE_CONTENT_WRITER`, declares final `OstreeContentWriter` deriving from `GOutputStream`, exposes `_ostree_content_writer_new()` with repo/checksum/uid/gid/mode/content length/xattrs, and `ostree_content_writer_finish()`.

## Control Flow
No runtime flow in the header.

## State and Persistence
Implementation state tracks an open bare repository content write until finish or cleanup.

## Dependencies and Integration Points
Includes `ostree-repo.h`, connecting the stream abstraction to repository storage.

## Risks
The constructor is internal, while finish is the required commit boundary. Callers must not assume close commits content.

## Test Signals
Compile/type checks and stream write/finish integration tests validate this declaration.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-content-writer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-core-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-core-private.h

## Purpose
Defines private constants, on-disk stream format types, and helper prototypes for libostree's core object serialization and validation layer.

## Important APIs and Types
Declares default archive compression level, default file/directory modes, file header variant signatures, object path helpers, static delta path helpers, xattr canonicalization/validation, stat/GFileInfo conversion, bare-user-only mode validation, metadata validation/verification, raw-to-archive stream conversion, timestamp comparison, default sysroot path, and optional detached GPG signature appending.

## Control Flow
No implementation flow. Inline helpers convert checksum variants to strings, derive commitpartial paths, and identify bare repository modes.

## State and Persistence
The header documents persistent OSTree file object stream formats: a big-endian length-prefixed `GVariant` header followed by content, with a zlib variant including uncompressed size. These formats are read by multiple implementation files.

## Dependencies and Integration Points
Includes `ostree-core.h`, `otutil.h`, and `<sys/stat.h>`. It is shared by repo commit, checkout, pull, fsck, static delta, and content conversion code.

## Risks
Changing variant signatures or object path helpers is repository-format breaking. Helpers marked private are still widely coupled inside libostree, so changes require broad integration tests.

## Test Signals
Tests should cover file header round trips, object/static-delta path generation, checksum conversion, xattr canonicalization, metadata schema validation, and downgrade timestamp checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-core-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-core.c -->
# sources/cloud-native/ostree/src/libostree/ostree-core.c

## Purpose
Implements repository-independent OSTree core data-format helpers: ref/checksum validation, file object stream creation/parsing, checksum calculation, object name/path conversion, metadata schema validation, commit metadata helpers, static delta path helpers, and default sysroot/version utilities.

## Important APIs and Types
Major exported or internal APIs include `ostree_parse_refspec()`, ref/remote/collection/checksum validators, `_ostree_file_header_new()`, `_ostree_zlib_file_header_new()`, `ostree_raw_file_to_content_stream()`, archive-z2 stream conversion functions, `ostree_content_stream_parse()`, content file parse wrappers, `ostree_break_hardlink()`, xattr retrieval, checksum file APIs including async variants, object type/name serialization helpers, checksum hex/base64 conversion helpers, `_ostree_loose_path()`, relative object/static-delta paths, `_ostree_parse_delta_name()`, metadata validators, commit getters, `OstreeCommitSizesEntry`, `_ostree_compare_timestamps()`, optional GPG signature append, `_ostree_get_default_sysroot_path()`, and `ostree_check_version()`.

## Control Flow
The file first validates ABI enum values, builds cached regexes for refs/remotes, canonicalizes xattrs by sorting, serializes file headers as 4-byte big-endian length plus 4-byte padding plus big-endian `GVariant`, chains headers with content streams, and parses streams by reading the header, validating size, decoding metadata, and optionally wrapping compressed content in a zlib decompressor. Checksum functions hash metadata headers and regular-file streams according to object type. Metadata verification hashes the normalized variant bytes, compares the expected checksum, then validates commit/dirtree/dirmeta structure.

## State and Persistence
Persistent formats include loose object paths, static delta paths, commit/dirtree/dirmeta variants, dirmeta xattrs, file object headers, and commit `ostree.sizes` entries. Runtime cached state is limited to regex singletons and a default sysroot `GFile` initialized from `OSTREE_SYSROOT`.

## Dependencies and Integration Points
Depends on libglnx, `ostree-chain-input-stream`, varint helpers, checksum utilities from `otutil`, GIO Unix streams, zlib converters, GLib variants, stat/xattr APIs, and many public `ostree-core.h` type definitions. It is central to repo commit, pull, checkout, fsck, static deltas, and deployment downgrade protection.

## Risks
This file is format-critical: endian conversions, header length/padding, xattr sorting, and checksum semantics must remain stable. `trusted` parsing affects `GVariant` validation assumptions. `_ostree_validate_structureof_xattrs()` increments the loop index inside the loop as well as in the `for`, which can skip entries and deserves scrutiny. Ref/checksum validation rejects uppercase hex and leading punctuation by design, which can affect compatibility.

## Test Signals
Strong signals include golden object checksum tests, file header parse/serialize round trips for regular files and symlinks, compressed archive stream tests, xattr ordering/duplicate validation, dirtree path traversal rejection, static delta path fixtures, async checksum parity, hardlink break behavior, commit size metadata parsing, timestamp downgrade checks, and fsck/pull metadata verification integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-core.c -->
