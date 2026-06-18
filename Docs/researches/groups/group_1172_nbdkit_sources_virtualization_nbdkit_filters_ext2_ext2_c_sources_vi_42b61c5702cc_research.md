# Group Research: group_1172_nbdkit_sources_virtualization_nbdkit_filters_ext2_ext2_c_sources_vi_42b61c5702cc

Scope: `Docs/research_subset_a.md` includes `sources/virtualization/nbdkit`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/ext2/ext2.c -->
# File Research: sources/virtualization/nbdkit/filters/ext2/ext2.c

Implements the `nbdkit ext2` filter, exposing a regular file inside an ext2-family filesystem image as the NBD export. The required `ext2file=` parameter is either an absolute in-image path or `exportname`, in which case each client export name selects the embedded file.

The filter opens one shared ext2 filesystem in `.after_fork` using `ext2fs_open()` with the custom `nbdkit_io_manager` from `io.c`. The underlying plugin is opened through `nbdkit_next_context_open()` once, then bound into per-client filter contexts with `nbdkit_context_set_next()` during `.prepare`.

Per-connection handles store the export name, resolved inode, ext2 file handle, and nbdkit context. `ext2_prepare()` resolves paths through `ext2fs_namei()`, rejects non-regular files, opens the file with optional `EXT2_FILE_WRITE`, and does not follow symlinks.

Reads and writes loop through `ext2fs_file_llseek()`, `ext2fs_file_read()`, and `ext2fs_file_write()`. FUA is advertised as native and implemented by `ext2fs_file_flush()` after writes with `NBDKIT_FLAG_FUA`; flush also maps to `ext2fs_file_flush()`.

The filter disables multi-conn and serializes requests because libext2fs is not treated as re-entrant. Trim and optimized zero are not exposed to clients, but capability probes are used so libext2fs can use backend discard/zero internally through the I/O manager.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/ext2/ext2.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/ext2/io.c -->
# File Research: sources/virtualization/nbdkit/filters/ext2/io.c

Provides a libext2fs `io_manager` backed by nbdkit `next` callbacks rather than POSIX file descriptors. It is derived from e2fsprogs `unix_io.c` and adapts ext2fs block I/O to NBD byte-range operations.

`nbdkit_io_encode()` and `nbdkit_io_decode()` pass an `nbdkit_next *` through libext2fs as a pseudo-device name of the form `nbdkit:%p`. `io_open()` decodes this pointer, allocates an ext2fs `io_channel`, stores the backend, initializes a 1024-byte block size, and rejects read-write opens when the backend cannot write.

Raw block reads and writes convert block/count requests into byte sizes and offsets, including the ext2fs convention that negative counts mean byte counts. They call `next->pread()` and `next->pwrite()` and maintain ext2fs I/O stats.

The manager implements close, block-size setting, byte writes, flush, `offset` option parsing, discard, optional cache readahead, and optional zeroout. Discard and zeroout are forwarded only when the backend advertises trim/zero support; unsupported cases return ext2fs unimplemented errors.

Several byte-size calculations carry TODO comments about possible 32-bit overflow when forwarding large counts to nbdkit callbacks.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/ext2/io.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/ext2/io.h -->
# File Research: sources/virtualization/nbdkit/filters/ext2/io.h

Declares the ext2 filter's custom libext2fs I/O bridge. It includes `ext2_io.h` and `nbdkit-filter.h`.

Defines `EXT2_ET_MAGIC_NBDKIT_IO_CHANNEL` using a reserved ext2fs magic value. Exports `nbdkit_io_encode()`, `nbdkit_io_decode()`, and the global `io_manager nbdkit_io_manager`.

This is the narrow interface between `ext2.c` and the backend-backed I/O manager in `io.c`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/ext2/io.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/extentlist/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/extentlist/Makefile.am

Automake rules for `nbdkit-extentlist-filter.la`. The filter sources are `extentlist.c` and the public nbdkit filter header.

The build uses top-level common rules, include paths for generated/public/common headers, replacement and utility libraries, module/shared libtool flags, the Windows import-library hook, and the optional shared filter linker version script.

When POD tooling is available, it builds `nbdkit-extentlist-filter.1` and corresponding HTML through `podwrapper.pl`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/extentlist/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/extentlist/extentlist.c -->
# File Research: sources/virtualization/nbdkit/filters/extentlist/extentlist.c

Implements an extent metadata override filter. The required `extentlist=<file>` parameter names a text file containing offset, length, and optional type fields.

`parse_extentlist()` runs at get-ready time, reads the file completely, skips blank/comment lines, parses sizes with `nbdkit_parse_size()`, and accepts either numeric extent types or strings containing `hole` and/or `zero`. Zero-length entries are ignored.

Parsed extents are sorted by offset, checked for overlap and overflow, then normalized so the final vector is ordered, non-overlapping, and gapless. Gaps are filled with synthetic `HOLE|ZERO` extents, including a trailing hole to `UINT64_MAX`.

`extentlist_extents()` binary-searches the normalized list for the requested offset and emits consecutive extents with `nbdkit_add_extent()` until the requested range is covered. The filter always advertises extents support and does not alter data I/O.

Notable behavior: duplicate `extentlist` or parse failures call `exit(EXIT_FAILURE)` in several paths rather than returning an nbdkit configuration error.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/extentlist/extentlist.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/fua/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/fua/Makefile.am

Automake rules for `nbdkit-fua-filter.la`. It builds `fua.c` with the public filter header.

The build uses nbdkit public/generated include paths, warning CFLAGS, module/shared libtool flags, the Windows import-library hook, and the optional common filter linker script. Man page generation is enabled through POD when available.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/fua/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/fua/fua.c -->
# File Research: sources/virtualization/nbdkit/filters/fua/fua.c

Implements a policy filter for Force Unit Access behavior. Configuration supports `fua-mode`/`fuamode` values `none`, `emulate`, `native`, `force`, `pass`, and `discard`, plus `flush-on-close`.

`fua_prepare()` validates requested behavior for writable connections: emulation requires flush support, native/force require backend FUA support, and flush-on-close requires flush support. Read-only connections skip these checks because the filter has no write-side effect.

`fua_can_flush()` and `fua_can_fua()` report capabilities according to the selected mode. `update_flags()` rewrites FUA flags for `pwrite`, `trim`, and `zero`: emulate strips FUA and flushes after success, force adds FUA, discard strips FUA, and pass/native leave flags unchanged.

`fua_flush()` passes through, no-ops when all writes are forced-FUA, or deliberately drops flushes in discard mode. `fua_finalize()` optionally flushes at connection close.

Notable bug: the config parser uses a standalone `if` for `"none"` followed by an `if`/`else if` chain for other values, so an explicit `fua-mode=none` falls through to the final unknown-mode error even though `NONE` is the default.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/fua/fua.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/gzip/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/gzip/Makefile.am

Automake rules for `nbdkit-gzip-filter.la`, built only when `HAVE_ZLIB` is true. The filter source is `gzip.c` plus the public nbdkit filter header.

The rule includes nbdkit public/generated/common headers, replacement and utility paths, warning and zlib CFLAGS, utility/replacement libraries, zlib libraries, Windows import-library support, and optional linker version script support.

When POD tooling is available, it generates `nbdkit-gzip-filter.1` and HTML documentation through `podwrapper.pl`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/gzip/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/gzip/gzip.c -->
# File Research: sources/virtualization/nbdkit/filters/gzip/gzip.c

Implements a read-only gzip expansion filter by fully inflating the underlying plugin into a temporary file on first prepare. A global mutex ensures only one thread performs decompression.

The filter always opens the backend read-only. `do_uncompress()` obtains the compressed size, creates an unlinked temporary file under `$TMPDIR` or `LARGE_TMPDIR`, initializes zlib with gzip-header support via `inflateInit2(16+MAX_WBITS)`, reads compressed data from `next->pread()` in 4 MiB chunks, and writes all decompressed output to the temp file.

The uncompressed size is known only after full inflation and is cached globally. `gzip_get_size()` checks that the underlying compressed size has not changed since inflation and reports the cached uncompressed size.

Client reads are served from the temporary file with `pread()`. The filter disables writes and extents, advertises cache emulation, and reports multi-conn consistency because all clients read the same inflated temp file.

This design favors simplicity and random read performance after startup, but requires temporary storage for the entire uncompressed image.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/gzip/gzip.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/indexed-gzip/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/indexed-gzip/Makefile.am

Automake rules for `nbdkit-indexed-gzip-filter.la`, built only when `HAVE_ZLIB` is true. Sources include `indexed_gzip.c`, `ig_handle.h`, `ig_zran.c/.h`, and `zran.c/.h`.

The build uses nbdkit public/generated/common/replacement/utility include paths, warning and zlib CFLAGS, utility and replacement libraries, zlib libraries, `-lm`, Windows import-library support, and optional filter linker version script support.

When POD tooling is available, it generates `nbdkit-indexed-gzip-filter.1` and HTML documentation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/indexed-gzip/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/indexed-gzip/ig_handle.h -->
# File Research: sources/virtualization/nbdkit/filters/indexed-gzip/ig_handle.h

Defines the per-connection handle for the indexed-gzip filter. The handle stores a `struct deflate_index *index` and the cached compressed size of the upstream nbdkit layer.

The header includes zlib, nbdkit filter APIs, common utility headers, and standard headers used by the indexed-gzip implementation.

This struct is shared by `indexed_gzip.c` and `ig_zran.c`, coupling nbdkit connection state to the reusable zran index/extract logic.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/indexed-gzip/ig_handle.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/indexed-gzip/ig_zran.c -->
# File Research: sources/virtualization/nbdkit/filters/indexed-gzip/ig_zran.c

Adapts Mark Adler's zran random-access deflate indexing example to nbdkit I/O. Instead of `FILE *` reads, it uses `next->pread()` and returns `Z_NBDKIT_ERROR` when nbdkit has populated an error value.

`ig_deflate_index_build()` makes one pass over the compressed stream, detects raw/zlib/gzip mode, initializes zlib, inflates with `Z_BLOCK`, and records access points when a block boundary is reached after the configured uncompressed span. Access points store compressed offset, uncompressed offset, bit offset, and up to a 32 KiB dictionary window.

The build path supports concatenated gzip members by resetting the inflate state at member boundaries. On success, it stores the index and uncompressed length in the connection handle.

`ig_deflate_index_extract()` binary-searches for the nearest access point at or before the requested offset, resets the reusable zlib stream, primes partial-byte state when needed, installs the saved dictionary, discards uncompressed data until the target offset, and then inflates into the caller buffer.

The implementation serializes extraction at the filter level because the reusable `z_stream` in the index is mutated during reads. Multi-member gzip handling is present but intricate, including manual trailer discard and header-skipping paths.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/indexed-gzip/ig_zran.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/indexed-gzip/ig_zran.h -->
# File Research: sources/virtualization/nbdkit/filters/indexed-gzip/ig_zran.h

Declares the nbdkit-adapted zran functions. It includes `ig_handle.h` and `zran.h`.

Defines `Z_NBDKIT_ERROR` as `-99`, outside zlib's normal negative error range, so callers can distinguish backend I/O failures from zlib errors while using the separate nbdkit error output parameter.

Documents `ig_deflate_index_build()` as the nbdkit-backed equivalent of `deflate_index_build()`, building access points roughly every configured span bytes of uncompressed output.

Documents `ig_deflate_index_extract()` as the nbdkit-backed equivalent of `deflate_index_extract()`, reading a requested uncompressed byte range through an existing deflate index.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/indexed-gzip/ig_zran.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/indexed-gzip/indexed_gzip.c -->
# File Research: sources/virtualization/nbdkit/filters/indexed-gzip/indexed_gzip.c

Implements the `indexed-gzip` filter, a read-only gzip/deflate expansion filter using a persistent random-access index instead of inflating the whole image to a temp file.

Configuration requires `gzip-index-path=<PATH>` and accepts `gzip-index-span=<SIZE>`, defaulting to 1 MiB. The span controls index density and the average amount of data decompressed per random read.

Each connection opens the backend read-only, allocates a handle, caches compressed size in `.prepare`, then either deserializes an existing index file or builds a new one with `ig_deflate_index_build()` and writes it with `deflate_index_serialize()`.

The filter reports the uncompressed size from `h->index->length`, disables writes and extents, advertises cache emulation and multi-conn consistency, and serves reads through `ig_deflate_index_extract()`.

A global mutex serializes reads because extraction mutates the zlib stream stored in the index. The index file is a raw binary serialization of host C types, so it is tied to host ABI/endianness and is not a portable interchange format.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/indexed-gzip/indexed_gzip.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/indexed-gzip/zran.c -->
# File Research: sources/virtualization/nbdkit/filters/indexed-gzip/zran.c

Provides shared zran index management support plus an optional standalone test program under `#ifdef TEST`. The comments preserve Mark Adler's version history and explain random access to deflate streams through block-boundary access points and saved dictionaries.

`deflate_index_free()` releases all access-point dictionary windows, the access-point list, the reusable zlib stream, and the index object. `add_point()` grows the access-point array, records compressed/uncompressed offsets and bit state, and copies the appropriate rolling dictionary window.

`deflate_index_serialize()` writes the index header and each access point using raw `fwrite()` of C scalar types followed by dictionary bytes. `deflate_index_deserialize()` reconstructs the index, initializes a raw inflate stream, validates broad header and point bounds, allocates each dictionary window, and returns NULL on malformed or truncated input.

The optional `main()` can build or load an index for a local file, extract a sample range, and save the index. In the filter build, the reusable pieces are used by `indexed_gzip.c` and `ig_zran.c`.

The serialization deliberately does not include zlib stream state and is host-format dependent.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/indexed-gzip/zran.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/indexed-gzip/zran.h -->
# File Research: sources/virtualization/nbdkit/filters/indexed-gzip/zran.h

Defines the core zran data structures and constants. `WINSIZE` is 32 KiB, `CHUNK` is 16 KiB, and compression modes are the zlib `inflateInit2()` window-bits values for raw, zlib, and gzip streams.

`point_t` stores one random-access point: uncompressed offset, compressed file offset, partial-bit count, dictionary length, and dictionary bytes. `struct deflate_index` stores the access-point count, stream mode, uncompressed length, access-point array, and reusable `z_stream`.

Declares index free, serialize, deserialize, and internal access-point append helpers. The comments state that raw serialization is tied to system endianness.

When `NOPRIME` is defined, the header supplies an `inflatePrime()` substitute using synthetic empty deflate blocks; otherwise `INFLATEPRIME` maps directly to zlib `inflatePrime`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/indexed-gzip/zran.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/ip/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/ip/Makefile.am

Automake rules for `nbdkit-ip-filter.la`. Sources are `ip.c`, `rules.c`, `rules.h`, and the public nbdkit filter header.

The build uses public/generated/common/replacement/utility include paths, warning CFLAGS, utility and replacement libraries, Windows import-library support, module/shared libtool flags, and optional linker version script support.

When POD tooling is available, it generates `nbdkit-ip-filter.1` and HTML documentation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/ip/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/ip/ip.c -->
# File Research: sources/virtualization/nbdkit/filters/ip/ip.c

Implements the top-level `ip` access-control filter. It stores allow and deny rule lists, parses repeated `allow=` and `deny=` parameters through `parse_rules()`, and frees rule lists at unload.

The filter normally checks clients during `.preconnect`, before heavy NBD/TLS negotiation. If any rule depends on TLS distinguished names, `rules.c` sets `late_filtering=true`, causing checks to move to `.list_exports` and `.open`, where TLS peer information is available.

`check_if_allowed()` enforces the rule result. Rejected clients fail with a source-address restriction error. The filter passes through to the next backend only after the access check succeeds.

Rule order semantics are allow-list first, deny-list second, default allow if no rule matches.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/ip/ip.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/ip/rules.c -->
# File Research: sources/virtualization/nbdkit/filters/ip/rules.c

Implements parsing, debugging, matching, and evaluation of IP filter rules. Rule types include any IPv4/IPv6, loopback variants, CIDR IPv4/IPv6, Unix sockets, TLS DN and issuer DN globs, Unix peer pid/uid/gid, peer security context, and VSOCK cid/port rules.

`parse_rule()` appends rules to a linked list and accepts comma-separated lists, except `dn:` and `issuer-dn:` values are parsed as whole strings because DNs may contain commas. IP addresses use `inet_pton()`, prefixes are range-checked, numeric IDs are parsed and bounded, and security labels are copied.

TLS DN matching uses `fnmatch()` with case-folding when available. Unix identity rules only match `AF_UNIX`; VSOCK rules are compiled conditionally; security context matching can apply to Unix, IPv4, and IPv6 peers.

`check_if_allowed()` obtains the peer address with `nbdkit_peer_name()`, fails closed if that lookup fails, optionally logs peer details, returns true on the first matching allow rule, false on the first matching deny rule, and true if no rules match.

Potential issue: IPv4 prefix matching computes `0xffffffff << (32 - prefixlen)`, which is undefined for prefix length 0 in C, even though `/0` is accepted by the parser.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/ip/rules.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/ip/rules.h -->
# File Research: sources/virtualization/nbdkit/filters/ip/rules.h

Declares the IP filter rule interface. It forward-declares `struct rule` and exposes the global `late_filtering` flag.

Exports helpers to print, free, parse, and evaluate rule lists: `print_rules()`, `free_rules()`, `parse_rules()`, and `check_if_allowed()`.

This header separates the access-control policy engine in `rules.c` from the nbdkit callback wiring in `ip.c`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/ip/rules.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/limit/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/limit/Makefile.am

Automake rules for `nbdkit-limit-filter.la`. It builds `limit.c` with the public nbdkit filter header.

The build uses public/generated/common/utility include paths, warning CFLAGS, utility and replacement libraries, Windows import-library support, module/shared libtool flags, and optional linker version script support.

When POD tooling is available, it generates `nbdkit-limit-filter.1` and HTML documentation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/limit/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/limit/limit.c -->
# File Research: sources/virtualization/nbdkit/filters/limit/limit.c

Implements a client connection limit filter. The `limit=<unsigned>` parameter sets the maximum concurrent open clients; `0` disables limiting. The default limit is 1.

A mutex protects the global connection counter. `.preconnect` checks the current count early, after passing through lower preconnect logic, so excess clients are rejected before heavier negotiation proceeds.

`.open` checks again before incrementing because clients may delay negotiation between preconnect and open. `.close` decrements the counter.

The filter returns `NBDKIT_HANDLE_NOT_NEEDED` for accepted clients and otherwise has no effect on data path behavior.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/limit/limit.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/log/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/log/Makefile.am

Automake rules for `nbdkit-log-filter.la`. The filter is disabled on Windows because it requires `open_memstream()`.

Sources are `log.c`, `log.h`, `output.c`, and the public nbdkit filter header. The build uses public/generated/common/utility include paths, warning CFLAGS, utility library linkage, Windows import-library hook, module/shared libtool flags, and optional linker version script support.

When POD tooling is available, it generates `nbdkit-log-filter.1` and HTML documentation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/log/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/log/log.c -->
# File Research: sources/virtualization/nbdkit/filters/log/log.c

Implements the nbdkit log filter callback surface. Configuration accepts `logfile=`, `logappend=`, and `logscript=`. At get-ready, it opens the log file if requested, records the process id, and logs readiness with the thread model.

The filter logs lifecycle and negotiation events: fork, list exports, preconnect, connect, disconnect, and transaction counts. On connect, it queries and logs backend size, block sizes, and capabilities such as write, flush, rotational, trim, zero, FUA, extents, cache, and fast-zero.

Data-path methods wrap reads, writes, flushes, trims, zeroes, extents, and cache calls. Each operation logs entry and exit with a per-connection monotonically increasing id. Extent and export listing methods expand returned metadata into structured log strings.

The filter is observational: it forwards all operations unchanged and records return values/errors. It uses assertions to document expected flag sets for each callback.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/log/log.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/log/log.h -->
# File Research: sources/virtualization/nbdkit/filters/log/log.h

Defines shared state and helpers for the log filter. `log_id_t` is a `uint64_t`, and each handle stores connection id, per-connection transaction id, export name, and TLS state.

Declares global logging configuration and the shared mutex. `get_id()` increments the per-connection id under the mutex.

Declares `enter()`, `leave()`, `print()`, `leave_simple()`, and `leave_simple2()`. The `LOG` macro uses GCC cleanup attributes to automatically log a simple leave record on function exit, reducing duplicated exit-path logging code.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/log/log.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/log/output.c -->
# File Research: sources/virtualization/nbdkit/filters/log/output.c

Implements output backends for the log filter. `to_file()` writes timestamped log lines to the configured `FILE *`, including connection id, action, optional transaction id, formatted arguments, and enter/leave markers. It uses `flockfile()`/`funlockfile()` when available and flushes each line.

`to_script()` builds a small shell program in memory containing variables such as `act`, `connection`, `type`, and `id`, appends the configured script body, and runs it with `system()`. Script exit status is converted to nbdkit error logging but otherwise ignored.

`enter()`, `leave()`, and `print()` dispatch to the file and/or script output backends. `leave_simple()` maps nbdkit-visible errno values to protocol error names and logs a uniform `return=<n> error=<name>` result. `leave_simple2()` is the cleanup-attribute adapter used by the `LOG` macro.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/log/output.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/luks/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/luks/Makefile.am

Automake rules for `nbdkit-luks-filter.la`, built only when `HAVE_GNUTLS_PBKDF2` is true. Sources are `luks.c`, `luks-encryption.c`, `luks-encryption.h`, and the public nbdkit filter header.

The build uses public/generated/common/replacement/utility include paths, warning and GnuTLS CFLAGS, utility and replacement libraries, GnuTLS libraries, Windows import-library support, module/shared libtool flags, and optional linker version script support.

When POD tooling is available, it generates `nbdkit-luks-filter.1` and HTML documentation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/luks/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/luks/luks-encryption.c -->
# File Research: sources/virtualization/nbdkit/filters/luks/luks-encryption.c

Implements LUKSv1 header parsing, keyslot unlocking, and sector encryption/decryption support for the LUKS filter. It defines packed LUKSv1 header and keyslot structures, constants for magic, salts, key slots, stripes, and keyslot alignment.

Supported cipher parsing is intentionally narrow: AES with CBC or XTS through GnuTLS, hash algorithms supported by GnuTLS, and IV generation `plain` or `plain64`. ESSIV-related code is present but disabled. Header cipher strings are split from the LUKS `cipher_mode` field and mapped to GnuTLS cipher identifiers.

`load_header()` validates disk size, magic, version 1, byte-swaps big-endian header fields, bounds-checks payload offset, key length, iterations, keyslot state, stripe count, and key-material offsets. It logs UUID and enabled keyslot ranges before trying to unlock.

`try_passphrase_in_keyslot()` derives a candidate key with PBKDF2, reads encrypted split key material, decrypts it, merges anti-forensic stripes with `afmerge()`, derives and compares the master-key digest, and stores the master key on success.

`create_cipher()` initializes a GnuTLS cipher with the unlocked master key. `do_decrypt()` and `do_encrypt()` calculate a per-sector IV, set it on the cipher, and perform in-place sector-sized cryptographic transforms.

Notable issue: `cipher_alg_iv_len()` contains `if (CIPHER_MODE_ECB)` instead of checking the `mode` argument, so it always returns 0. That appears to suppress IV allocation/use for all modes, which is inconsistent with CBC/XTS sector encryption expectations.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/luks/luks-encryption.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/luks/luks-encryption.h -->
# File Research: sources/virtualization/nbdkit/filters/luks/luks-encryption.h

Declares the LUKSv1 encryption helper interface. The header notes that LUKSv2 is not supported and defines `LUKS_SECTOR_SIZE` as 512.

Forward-declares `struct luks_data` and exports `load_header()`, `free_luks_data()`, `get_payload_offset()`, `create_cipher()`, `do_decrypt()`, and `do_encrypt()`.

The API separates LUKS metadata/key handling from the nbdkit filter callback implementation in `luks.c`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/luks/luks-encryption.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/luks/luks.c -->
# File Research: sources/virtualization/nbdkit/filters/luks/luks.c

Implements the nbdkit LUKS filter, exposing decrypted payload data from a LUKSv1 encrypted backend. Configuration requires `passphrase=<SECRET>`, read through `nbdkit_read_password()`.

Each connection allocates a handle and calls `load_header()` in `.prepare` to parse the header and unlock the master key. The passphrase and master key are zeroed before free where possible, though comments note they should ideally be held in mlocked memory.

`luks_get_size()` subtracts the LUKS payload offset from the backend size. The filter disables extents and trim, asks nbdkit to emulate zeroes through writes, disables fast-zero, advertises cache emulation, and adjusts block-size constraints to at least 512 bytes.

Reads translate cleartext offsets to encrypted payload sectors, read full sectors from the backend, decrypt them, and copy requested bytes for unaligned heads/tails. Writes encrypt sector-sized blocks; unaligned writes use read-modify-write protected by a global mutex.

The filter passes backend write flags through to the underlying `pread()`/`pwrite()` calls and creates a fresh GnuTLS cipher handle for each read or write operation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/luks/luks.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/lzip/Makefile.am -->
# File Research: sources/virtualization/nbdkit/filters/lzip/Makefile.am

Automake rules for `nbdkit-lzip-filter.la`, built only when `HAVE_LZMA_LZIP_DECODER` is true. Sources are `lzip.c`, `lzipfile.c/.h`, `lzipindex.c/.h`, a symlinked `blkcache.c` from the xz filter, xz `blkcache.h`, and the public nbdkit filter header.

The symlinked `blkcache.c` workaround exists because older Automake/subdir-objects behavior made directly sharing the C file problematic in some environments.

The build uses public/generated/xz/common/utility include paths, warning and liblzma CFLAGS, liblzma, utility and replacement libraries, Windows import-library support, module/shared libtool flags, and optional linker version script support.

When POD tooling is available, it generates `nbdkit-lzip-filter.1` and HTML documentation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/lzip/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/lzip/lzip.c -->
# File Research: sources/virtualization/nbdkit/filters/lzip/lzip.c

Implements a read-only lzip expansion filter using liblzma and a block cache shared with the xz filter. Configuration accepts `lzip-max-block=<SIZE>` and `lzip-max-depth=<N>`, defaulting to a 512 MiB maximum decompressed block and cache depth 8.

Each connection opens the backend read-only, allocates a `blkcache`, and opens/parses the lzip file in `.prepare`. Preparation rejects files whose largest decompressed member exceeds `lzip-max-block`.

The filter reports the combined uncompressed size from the lzip index, disables writes and extents, advertises cache emulation and multi-conn consistency, and serializes requests.

`lzip_pread()` looks up the member containing the requested offset in the cache; on a miss, it decompresses the whole lzip member through `lzipfile_read_block()` and inserts it into the cache. Requests spanning multiple members recurse to satisfy the remainder.

The design is efficient for multi-member lzip files with bounded member sizes, but can require allocating an entire decompressed member per cache miss.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/lzip/lzip.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/lzip/lzipfile.c -->
# File Research: sources/virtualization/nbdkit/filters/lzip/lzipfile.c

Abstracts liblzma and lzip container parsing for the lzip filter. It verifies lzip magic, builds a member index from lzip footers, tracks the largest uncompressed member, and reads/decompresses individual members.

`setup_index()` walks backward from end-of-file. For each member, it reads the 20-byte footer, decodes little-endian uncompressed data size and member size, checks bounds, moves to the member start, verifies the lzip header magic, and prepends the member into the index.

After finalization, `lzipfile_open()` logs combined uncompressed size, member count, largest member size, and indexable block size. `lzipfile_get_size()` returns the combined uncompressed size.

`lzipfile_read_block()` finds the member containing a requested uncompressed offset, initializes an lzip decoder with `lzma_lzip_decoder()`, allocates the full uncompressed member buffer, streams compressed data from `next->pread()` in 1 MiB chunks, and returns the decompressed member plus its uncompressed start/size.

Errors clean up the decoder, compressed buffer, and decompressed data buffer.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/lzip/lzipfile.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/lzip/lzipfile.h -->
# File Research: sources/virtualization/nbdkit/filters/lzip/lzipfile.h

Declares the opaque `lzipfile` interface used by `lzip.c`. It exposes open, close, largest-block-size, total-size, and block-read operations.

`lzipfile_read_block()` returns a newly allocated decompressed block containing the requested uncompressed offset and reports that block's uncompressed start and size. The caller owns the returned buffer.

The header keeps liblzma/container details out of the filter callback file.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/lzip/lzipfile.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/lzip/lzipindex.c -->
# File Research: sources/virtualization/nbdkit/filters/lzip/lzipindex.c

Implements the lzip member index. `lzip_index_prepend()` appends a member to the internal vector while the archive is scanned backward, so the stored list is in reverse order.

`lzip_index_finalize()` walks the reversed list, computes each member's uncompressed `data_offset`, total `combined_data_size`, and an `indexable_data_size` optimization when all non-final blocks have the same uncompressed size.

`lzip_index_search()` finds the member containing an uncompressed offset. If `indexable_data_size` is set, it computes the member index in constant time; otherwise it uses the generated vector binary-search helper with a custom comparator.

`lzip_index_destroy()` resets the vector and zeroes the struct.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/lzip/lzipindex.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/filters/lzip/lzipindex.h -->
# File Research: sources/virtualization/nbdkit/filters/lzip/lzipindex.h

Defines the lzip member index data structures. `lzip_index_member` maps one compressed archive member to its uncompressed data range and compressed file range.

`lzip_index` stores total uncompressed size, optional fixed uncompressed block size for O(1) lookup, and a vector of members stored in reverse order. The comments explain that random access works best for multi-member archives produced by tools such as `plzip`.

Declares `lzip_index_prepend()`, `lzip_index_finalize()`, `lzip_index_search()`, and `lzip_index_destroy()`.

This header provides the data model behind `lzipfile.c`'s backward footer scan and `lzip.c`'s random-read behavior.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/filters/lzip/lzipindex.h -->