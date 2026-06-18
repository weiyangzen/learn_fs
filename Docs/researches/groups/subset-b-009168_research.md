# subset-b-009168 research

Grouped research report for rsync I/O, integer/type helpers, portability shims, digest code, permission formatting, pool allocation, and fallback printf/address routines. Each section title preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/io.c -->
# sources/sync-backup/rsync/io.c

Purpose: implements rsync's socket/pipe I/O core: buffered circular input/output, rsync's multiplexed message stream, protocol integer/string encodings, keepalive and timeout enforcement, files-from forwarding, write-batch monitoring, and checksum-header serialization.

Important APIs/types/functions: global state includes `iobuf`, `sock_f_in`, `sock_f_out`, `total_data_read`, `total_data_written`, `csum_length`, `allowed_lull`, `kluge_around_eof`, `got_kill_signal`, `redo_list`, and `hlink_list`. Public entry points include `io_set_sock_fds`, `set_io_timeout`, `io_start_buffering_in/out`, `io_end_buffering_in/out`, `io_start_multiplex_in/out`, `io_end_multiplex_in/out`, `read_buf`, `write_buf`, `read_int`, `read_varint`, `read_varlong`, `read_int_bounded`, `read_varint_bounded`, `read_varint_size`, `read_longint`, `write_int`, `write_varint`, `write_varlong`, `write_longint`, `read_sum_head`, `write_sum_head`, `read_ndx`, `write_ndx`, `send_msg`, `send_msg_int`, `send_msg_success`, `read_args`, `read_line`, `wait_for_receiver`, `maybe_send_keepalive`, `maybe_flush_socket`, `start_filesfrom_forwarding`, `start_flist_forward`, `stop_flist_forward`, `start_write_batch`, and `stop_write_batch`.

Control flow: non-socket reads/writes go through `safe_read` and `safe_write`, which select with timeout checks and treat unexpected EOF as stream errors. Socket I/O goes through `perform_io`, which services circular input, raw output, and message output in one select loop. For multiplexed output it reserves a four-byte `MSG_DATA` header in `iobuf.out`, fills that header when raw data is ready to flush, prioritizes in-progress raw data, then queued messages, then remaining raw data. For multiplexed input, `read_buf` loops until a `MSG_DATA` payload is available, while `read_a_msg` consumes message headers and dispatches side-channel events such as stats, redo/no-send/success statuses, IO errors, timeout negotiation, delete logs, log forwarding, and error-exit propagation. File-list forwarding is layered into the same loop: `forward_filesfrom_data` normalizes CR/LF to NUL, collapses empty entries, optionally converts charset data, tracks implied includes, and writes data toward the sender while normal file-list input is being read.

State and persistence behavior: state is process-local and mostly global. `iobuf.in`, `iobuf.out`, and `iobuf.msg` are circular buffers with position/length fields plus raw boundary markers that allow multiplexed raw payloads to coexist with message headers. `last_io_in` and `last_io_out` drive timeout/keepalive decisions. `active_filecnt` and `active_bytecnt` throttle remove-source-file work. `redo_list` and `hlink_list` persist deferred file-list indexes in memory. Write-batch persistence is opt-in: `start_write_batch` records protocol version, compatibility flags, and checksum seed, then mirrors monitored input or output bytes to `batch_fd`.

Dependencies/integration: this file is tightly integrated with rsync's protocol definitions (`MSG_*`, `MPLEX_BASE`, `NDX_*`), logging and cleanup (`rprintf`, `rwrite`, `exit_cleanup`, `_exit_cleanup`), file-list machinery (`recv_file_list`, `flist_for_ndx`, `send_extra_file_list`, hard-link matching), delete logging, checksum metadata (`struct sum_struct`), iconv conversion, bandwidth limiting, batch mode, daemon/list-only compatibility paths, and statistics accounting.

Risks/test signals: the most sensitive logic is the circular buffer boundary accounting, multiplexed header reservation, `raw_input_ends_before`/`raw_flushing_ends_before` wraparound, and reentrancy while forwarding messages. Protocol hardening exists in bounded integer/size readers and checksum-header validation; tests should exercise malformed lengths, negative sizes, large checksum counts, short/overflowing vstrings, and invalid multiplex tags. Runtime regression signals include transfer hangs under bidirectional writes, unexpected EOF handling, stale keepalives, bwlimit drift, batch replay divergence, delete/status message forwarding errors, and old-protocol compatibility for `--files-from`, `--timeout`, `NDX_*`, and MD4/checksum headers.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/io.h -->
# sources/sync-backup/rsync/io.h

Purpose: provides protocol-version compatibility wrappers for integer and long integer wire encodings, hiding whether a caller should use legacy fixed-width encoding or protocol-30 varint encoding.

Important APIs/types/functions: `read_varint30`, `read_varlong30`, `write_varint30`, and `write_varlong30`. The header relies on external `protocol_version` and lower-level I/O functions declared elsewhere: `read_int`, `read_varint`, `read_longint`, `read_varlong`, `write_int`, `write_varint`, `write_longint`, and `write_varlong`.

Control flow: each inline helper branches on `protocol_version < 30`. Older peers use fixed `read_int`/`write_int` or sentinel-based `read_longint`/`write_longint`; protocol 30 and newer use compressed variable-length encodings, preserving the caller's `min_bytes` choice for long values.

State and persistence behavior: no local state or persistence. The only state dependency is the negotiated global protocol version, which must already be set before these helpers are used. These helpers directly affect on-the-wire compatibility and batch file reproducibility because they choose the byte layout for serialized integers.

Dependencies/integration: included by rsync code that wants version-neutral integer I/O. It integrates with `io.c`'s primitive encoders and with all protocol structures whose encoding changed at protocol 30.

Risks/test signals: the main risk is using these helpers before protocol negotiation or using raw integer helpers where a protocol-conditional helper is required. Tests should compare protocol 29 and 30+ streams, including boundary values that change encoded length and `min_bytes` values for long offsets.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/itypes.h -->
# sources/sync-backup/rsync/itypes.h

Purpose: defines small inline wrappers around `<ctype.h>` classification/conversion macros that safely cast through `unsigned char`, avoiding undefined behavior for negative `char` values.

Important APIs/types/functions: `isDigit`, `isHexDigit`, `isPrint`, `isSpace`, `isAlNum`, `isLower`, `isUpper`, `toLower`, and `toUpper`. Each accepts a `const char *` and applies the corresponding C library macro/function to the pointed byte.

Control flow: each helper is a single inline return statement. The pointer form lets calling code pass a cursor into a string without manually casting the dereferenced byte.

State and persistence behavior: no state and no persistence. Behavior depends on the active C locale for the underlying ctype functions, so classification can be locale-sensitive outside the ASCII range.

Dependencies/integration: included by general rsync parsing and formatting code, including numeric formatting in `compat.c`. It relies on `rsync.h` or surrounding includes to provide ctype declarations and integer typedefs.

Risks/test signals: callers must pass a valid pointer; there is no null or bounds check. Tests should include bytes with the high bit set on platforms where plain `char` is signed, and should consider locale-sensitive behavior if rsync expects ASCII-only parsing in a path.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/itypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/latest-year.h -->
# sources/sync-backup/rsync/latest-year.h

Purpose: centralizes the latest copyright/help year string for rsync-generated output.

Important APIs/types/functions: defines `LATEST_YEAR` as the string literal `"2026"`.

Control flow: no executable logic.

State and persistence behavior: no state or persistence. The macro is compile-time text consumed by other rsync sources.

Dependencies/integration: integrated wherever rsync prints version, copyright, or generated usage text that should carry the current project year.

Risks/test signals: the only practical risk is staleness. Release/build checks can grep generated version/help output for the expected year.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/latest-year.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/addrinfo.h -->
# sources/sync-backup/rsync/lib/addrinfo.h

Purpose: supplies missing `getaddrinfo`/`getnameinfo` constants, structs, and prototypes on platforms without full modern socket API support, using PostgreSQL-derived compatibility code.

Important APIs/types/functions: defines fallback `EAI_*`, `AI_*`, `NI_*`, `NI_MAXHOST`, `NI_MAXSERV`, `struct addrinfo`, and `struct sockaddr_storage` where missing. When `HAVE_GETADDRINFO` is absent, it macro-renames `getaddrinfo`, `freeaddrinfo`, `gai_strerror`, and `getnameinfo` to private `pg_*` names and declares them.

Control flow: preprocessor-only feature detection. The header avoids conflicts with partial system support: if headers lack `struct addrinfo`, rsync uses its local struct; if libc lacks functions, it exposes local implementations under renamed symbols.

State and persistence behavior: no runtime state. It shapes ABI expectations at compile time and therefore must match `lib/getaddrinfo.c` and all socket callers.

Dependencies/integration: included through rsync portability headers before socket code uses address-resolution APIs. It integrates with configure probes such as `HAVE_STRUCT_ADDRINFO`, `HAVE_GETADDRINFO`, and `HAVE_STRUCT_SOCKADDR_STORAGE`.

Risks/test signals: macro renaming can surprise code that expects system symbols, and the fallback constants may not match all platform-specific values. Build tests on systems with partial `getaddrinfo` support are important, as are socket tests for numeric host/service flags and canonical-name requests.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/addrinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/compat.c -->
# sources/sync-backup/rsync/lib/compat.c

Purpose: implements small portability replacements and human-readable number formatting helpers used across rsync.

Important APIs/types/functions: `get_number_separator`, `get_decimal_point`, optional fallback `getcwd`, optional fallback `waitpid`, optional fallback `memmove`, optional fallback `strpbrk`, optional fallback `strlcpy`, optional fallback `strlcat`, `sys_gettimeofday`, `do_big_num`, and `do_big_dnum`. Static `number_separator` caches the inferred thousands separator.

Control flow: configure macros include only missing libc replacements. `get_number_separator` formats `3.14` and chooses the opposite character of the locale decimal point for grouping. `do_big_num` rotates through four static buffers, optionally scales values into K/M/G/T/P units for human modes, otherwise emits digits backward with optional group separators and fractional suffix. `do_big_dnum` formats a double, and for human mode delegates integer/grouped rendering to `do_big_num`.

State and persistence behavior: state is limited to static formatting buffers and cached separator. Results are overwritten after four `do_big_num` calls or the next `do_big_dnum` call, so callers must copy if they need longer-lived strings. No persistent storage.

Dependencies/integration: includes `rsync.h` and `itypes.h`; used by logging, stats, and user-facing output helpers such as `big_num`. The portability shims integrate with configure results and old Unix libc behavior.

Risks/test signals: static buffers are not thread-safe, but rsync is process-oriented. `strlcat` assumes `bufsize - 1` is safe, so zero-size calls rely on unsigned behavior and should be tested if used. Human number formatting should be validated under locales with comma and dot decimal separators, negative `INT64_MIN`, and boundary values at 1000/1024 unit transitions.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/dummy.in -->
# sources/sync-backup/rsync/lib/dummy.in

Purpose: build-system placeholder that ensures the `lib` directory is created by configure when building from a VPATH tree.

Important APIs/types/functions: no APIs, types, or functions.

Control flow: no executable control flow; the file is build input data only.

State and persistence behavior: no runtime state. Its persistence is the presence of the file in the source tree so generated/configure output has a concrete directory member to copy or instantiate.

Dependencies/integration: used by the configure/build process, especially VPATH builds where empty directories may otherwise be absent.

Risks/test signals: risk is accidental deletion causing VPATH/configure directory creation regressions. Build tests should include an out-of-tree configure run.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/dummy.in -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/getaddrinfo.c -->
# sources/sync-backup/rsync/lib/getaddrinfo.c

Purpose: provides IPv4-only fallback implementations of `getaddrinfo`, `freeaddrinfo`, `gai_strerror`, and `getnameinfo` for platforms missing them.

Important APIs/types/functions: public `getaddrinfo`, `freeaddrinfo`, `gai_strerror`, and `getnameinfo`; helpers `check_hostent_err`, `canon_name_from_hostent`, `get_my_canon_name`, `get_canon_name_from_addr`, `alloc_entry`, `getaddr_info_single_addr`, `getaddr_info_name`, `gethostnameinfo`, and `getservicenameinfo`. Allocation hooks are `SMB_MALLOC` and `SMB_STRDUP`.

Control flow: `getaddrinfo` normalizes null hints, rejects unsupported families, defaults socket type to `SOCK_STREAM`, and routes to single-address handling for null/empty/numeric/passive nodes or to `gethostbyname` for hostnames. Single-address handling creates one `addrinfo` with `sockaddr_in` and may resolve a canonical name. Hostname handling creates one linked `addrinfo` per IPv4 address returned by `h_addr_list`. `getnameinfo` validates arguments and `AF_INET`, then formats hostname and/or service by reverse lookup unless numeric flags require direct numeric output.

State and persistence behavior: no global state. Each result list owns heap-allocated `addrinfo`, `sockaddr_in`, and optional canonical-name strings, released by `freeaddrinfo`.

Dependencies/integration: includes `rsync.h`, which pulls in `addrinfo.h` macro renames when needed. It uses legacy resolver APIs (`gethostbyname`, `gethostbyaddr`, `getservbyport`, `inet_pton`, `inet_ntoa`) and maps their errors to `EAI_*`.

Risks/test signals: fallback is IPv4-only, service parsing accepts only numeric strings via `atoi`, and `AI_NUMERICSERV` is incorrectly involved in canonical-name gating rather than service lookup. Resolver APIs used here are not thread-safe. Tests should cover passive null host, loopback fallback, numeric host rejection, multiple A records, canonical-name allocation failure paths, service buffer truncation, `NI_NAMEREQD`, and unsupported families.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/getaddrinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/getpass.c -->
# sources/sync-backup/rsync/lib/getpass.c

Purpose: implements `getpass` on systems that lack it, reading a password from `/dev/tty` or standard input while attempting to disable terminal echo and signal characters.

Important APIs/types/functions: public `getpass(const char *prompt)` and static `password[256]` buffer.

Control flow: the function opens `/dev/tty` for read/write and falls back to `stdin`/`stderr` if unavailable. It saves terminal attributes, clears `ECHO` and `ISIG`, prints a warning if echo could not be disabled, prompts, reads one line with `fgets`, prints a newline, restores terminal settings, closes the tty if opened, strips a trailing newline, and returns the static buffer or `NULL`.

State and persistence behavior: password contents persist in a static buffer until overwritten by the next call or process exit. No explicit zeroing is performed. Terminal state is restored on the normal path after reading.

Dependencies/integration: includes `stdio.h`, `string.h`, `termios.h`, and `rsync.h` for `BOOL`, `True`, and `False`. Used by authentication/password prompting code on deficient libc platforms.

Risks/test signals: fixed 256-byte buffer truncates longer passwords, disabling `ISIG` changes Ctrl-C behavior while reading, and abnormal termination before restore could leave terminal settings modified. Tests should use pseudo-terminals to verify echo restore, stdin fallback, newline stripping, EOF handling, and truncation behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/getpass.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/inet_ntop.c -->
# sources/sync-backup/rsync/lib/inet_ntop.c

Purpose: fallback `inet_ntop` implementation for formatting IPv4 and, when available, IPv6 binary addresses into presentation strings.

Important APIs/types/functions: public `inet_ntop`, static `inet_ntop4`, optional static `inet_ntop6`, and constants `NS_INT16SZ` and `NS_IN6ADDRSZ`.

Control flow: `inet_ntop` switches on address family, calling IPv4 or IPv6 helpers or setting `errno = EAFNOSUPPORT`. IPv4 uses `snprintf` into a dotted-quad temporary and checks destination capacity. IPv6 converts bytes to 16-bit words, finds the longest zero run for `::` compression, detects IPv4-embedded forms, formats hex groups, handles trailing zero compression, verifies capacity, and copies to the caller buffer.

State and persistence behavior: no state. All formatting uses caller-provided destination storage and stack temporaries.

Dependencies/integration: includes `rsync.h` for socket definitions, errno, `snprintf`, and assertions. Used by socket/address code when libc lacks `inet_ntop`.

Risks/test signals: IPv6 availability is gated by `AF_INET6` while `inet_pton.c` uses `INET6`, so configure consistency matters. Capacity checks must cover exact-fit destinations. Tests should compare system `inet_ntop` for IPv4, zero-compressed IPv6, IPv4-mapped IPv6, unsupported families, and too-small buffers.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/inet_ntop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/inet_pton.c -->
# sources/sync-backup/rsync/lib/inet_pton.c

Purpose: fallback `inet_pton` implementation for parsing IPv4 and optionally IPv6 presentation addresses into network-order binary form.

Important APIs/types/functions: public `inet_pton`, static `inet_pton4`, optional static `inet_pton6`, and constants `NS_INT16SZ`, `NS_INADDRSZ`, and `NS_IN6ADDRSZ`.

Control flow: `inet_pton` switches on address family, returning 1 for valid parse, 0 for invalid text, or -1 with `EAFNOSUPPORT`. IPv4 strictly accepts dotted decimal quads: four octets, no shorthand or hex, each <= 255, and destination untouched on failure. IPv6 parses hex groups, a single `::`, and embedded IPv4 tails, then expands the compressed zero run by shifting bytes manually before copying to destination.

State and persistence behavior: no state. Temporary parse buffers are stack-local and destination is only written after a complete valid parse.

Dependencies/integration: includes `rsync.h`; used by fallback address resolution and socket parsing on systems lacking libc support.

Risks/test signals: IPv4 parser allows leading zeros as decimal, not octal, which is intentional but may differ from `inet_aton`. IPv6 support is gated by `INET6`, not `AF_INET6`. Tests should cover invalid partial writes, multiple `::`, embedded IPv4, overflow groups, too few/many octets, unsupported families, and exact binary output.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/inet_pton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/md-defines.h -->
# sources/sync-backup/rsync/lib/md-defines.h

Purpose: central digest constants shared by C and assembly digest code.

Important APIs/types/functions: digest lengths `MD4_DIGEST_LEN`, `MD5_DIGEST_LEN`, `MAX_DIGEST_LEN`; block size `CSUM_CHUNK`; checksum algorithm IDs `CSUM_gone`, `CSUM_NONE`, `CSUM_MD4_ARCHAIC`, `CSUM_MD4_BUSTED`, `CSUM_MD4_OLD`, `CSUM_MD4`, `CSUM_MD5`, `CSUM_XXH64`, `CSUM_XXH3_64`, `CSUM_XXH3_128`, `CSUM_SHA1`, `CSUM_SHA256`, and `CSUM_SHA512`.

Control flow: preprocessor logic optionally undefines SHA digest lengths when disabled and chooses `MAX_DIGEST_LEN` from the strongest available configured digest length, falling back to MD5.

State and persistence behavior: no runtime state. Algorithm IDs are part of protocol/configuration semantics and must remain stable.

Dependencies/integration: included by `mdigest.h`, `md5.c`, and `md5-asm-x86_64.S`; also aligns with checksum negotiation code elsewhere in rsync.

Risks/test signals: changing IDs or digest sizes can break wire compatibility and buffer sizing. Build tests should cover OpenSSL/no-OpenSSL configurations, disabled SHA macros, and the assembly requirement that `CSUM_CHUNK == 64`.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/md-defines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/md5-asm-x86_64.S -->
# sources/sync-backup/rsync/lib/md5-asm-x86_64.S

Purpose: x86-64 optimized MD5 compression routine used when `USE_MD5_ASM` is enabled.

Important APIs/types/functions: exported `md5_process_asm(md_context *ctx, const void *data, size_t num)`, with Apple symbol aliasing to `_md5_process_asm`. The function expects the first four 32-bit words of `md_context` to be MD5 A/B/C/D state and processes `num` 64-byte blocks.

Control flow: under `USE_MD5_ASM`, the routine saves callee-saved registers, computes the end pointer from `num << 6`, loads A/B/C/D from the context, loops over each 64-byte block, performs all four MD5 rounds with inline constants, rotations, and message-word loads, adds the saved state to the transformed state, advances by 64 bytes, then writes A/B/C/D back and restores registers.

State and persistence behavior: mutates only the supplied digest context. It does not update bit counts or buffer state; `md5_update` in `md5.c` owns that surrounding state and calls this only for complete chunks.

Dependencies/integration: includes `config.h` and `md-defines.h`; called by `md5.c` when `USE_MD5_ASM` is set. The assembly comments state binary compatibility with OpenSSL-style MD5 context fields for the accessed words.

Risks/test signals: risks include ABI/register-save mistakes, context layout drift, endianness assumptions, and build portability across assemblers/Mach-O/Linux. Tests should compare MD5 vectors with and without `USE_MD5_ASM`, process multiple chunks and zero chunks, and run under sanitizers or ABI checkers where possible.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/md5-asm-x86_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/md5.c -->
# sources/sync-backup/rsync/lib/md5.c

Purpose: RFC 1321-compatible MD5 implementation used by rsync checksums when OpenSSL or another digest path is not used, with optional x86-64 assembly acceleration for full blocks.

Important APIs/types/functions: `md5_begin`, `md5_update`, `md5_result`, static `md5_process`, optional external `md5_process_asm`, static `md5_padding`, and `TEST_MD5` helpers/main.

Control flow: `md5_begin` initializes A/B/C/D and bit counters. `md5_update` updates byte counters, fills a partial 64-byte buffer if present, sends full blocks through assembly or `md5_process`, and stores any remainder. `md5_process` decodes 16 little-endian words and performs all four MD5 rounds using macros. `md5_result` appends padding and the 64-bit bit length, then writes the little-endian digest.

State and persistence behavior: all digest state lives in caller-owned `md_context`. `totalN` and `totalN2` track byte count overflow; `buffer` stores partial chunks. No persistent storage.

Dependencies/integration: includes `rsync.h` for `md_context`, integer helpers, and endian macros. Used from checksum code, and optionally paired with `md5-asm-x86_64.S`.

Risks/test signals: this is not suitable as a security primitive, but rsync uses it for checksums/protocol compatibility. Edge cases include length counter overflow, exact 56/64-byte padding boundaries, partial-buffer handling, assembly/C equivalence, and little-endian encoding macros. The file includes RFC 1321 test vectors under `TEST_MD5`.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/md5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/mdfour.c -->
# sources/sync-backup/rsync/lib/mdfour.c

Purpose: implements MD4 for legacy rsync checksum modes and SMB-derived compatibility behavior.

Important APIs/types/functions: public `mdfour_begin`, `mdfour_update`, `mdfour_result`, optional `mdfour` test helper, static global `m`, and helpers `mdfour64`, `copy64`, `copy4`, and `mdfour_tail`.

Control flow: `mdfour_begin` initializes MD4 state. `mdfour_update` assigns the global context pointer, processes full 64-byte chunks with `copy64` and `mdfour64`, updates bit counters for full chunks, and calls `mdfour_tail` for the final partial chunk or zero-length finalization. `mdfour_tail` pads into one or two 64-byte blocks, writes total bit count, and preserves the pre-protocol-27 behavior of omitting the high length word. `mdfour_result` writes little-endian A/B/C/D into the digest.

State and persistence behavior: digest state is caller-owned `md_context`, but compression uses a file-static `md_context *m`, making the implementation non-reentrant and not thread-safe. It also reads global `protocol_version` inside final padding, so the same input can hash differently for old protocol compatibility.

Dependencies/integration: includes `rsync.h`; used by checksum negotiation and legacy checksum paths. `TEST_MDFOUR` includes a standalone file checksum program and sets `protocol_version = 28`.

Risks/test signals: MD4 is cryptographically broken but retained for compatibility. Risks include the global context pointer, protocol-version-dependent finalization, and special handling for inputs whose length is a multiple of 64 in the test path. Tests should cover protocol 26 vs 27+ outputs, zero-length finalization, exact 55/56/64-byte boundaries, and concurrent/reentrant exclusion assumptions.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/mdfour.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/mdigest.h -->
# sources/sync-backup/rsync/lib/mdigest.h

Purpose: common digest header for rsync's MD4 and MD5 implementations, with optional OpenSSL SHA/EVP declarations and shared context layout.

Important APIs/types/functions: includes OpenSSL `sha.h`/`evp.h` when `USE_OPENSSL` is set, includes `md-defines.h`, defines `md_context` with A/B/C/D, two 32-bit counters, and a `CSUM_CHUNK` buffer, and declares `mdfour_*` and `md5_*` functions.

Control flow: no runtime logic; compile-time inclusion changes available external digest APIs.

State and persistence behavior: `md_context` is caller-owned mutable digest state. It is transient and not directly persisted, but its layout must match C and assembly code.

Dependencies/integration: consumed by checksum and digest implementation files. The context layout is relied on by `md5-asm-x86_64.S`, so field ordering is an ABI within the source tree.

Risks/test signals: changing `md_context` layout can break assembly. OpenSSL include availability must match configure defines. Build tests should cover `USE_OPENSSL` on/off and `USE_MD5_ASM` on/off, with digest-vector tests proving layout compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/mdigest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/permstring.c -->
# sources/sync-backup/rsync/lib/permstring.c

Purpose: converts a Unix `mode_t` into an `ls -l` style permission/type string.

Important APIs/types/functions: public `permstring(char *perms, mode_t mode)` and static permission map `"rwxrwxrwx"`.

Control flow: initializes the output buffer to `"----------"`, sets rwx bits by scanning the low nine permission bits, overlays setuid/setgid/sticky characters with uppercase variants when execute is absent, and sets the leading type character for directory, symlink, block, char, socket, FIFO, or regular/unknown file.

State and persistence behavior: no internal state. Caller owns an output buffer of at least `PERMSTRING_SIZE` bytes, including the trailing null.

Dependencies/integration: includes `rsync.h` for mode macros and `strlcpy`. Used by logging/generator/tls output paths that need human-readable modes.

Risks/test signals: correctness depends on platform `S_IS*` macros, and unsupported file types remain `-`. Tests should cover all type bits, all special permission combinations, no permissions, full permissions, and buffer-size contract with `PERMSTRING_SIZE`.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/permstring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/permstring.h -->
# sources/sync-backup/rsync/lib/permstring.h

Purpose: declares the permission-string buffer size and formatter API.

Important APIs/types/functions: `PERMSTRING_SIZE` is `11`, and `permstring(char *perms, mode_t mode)` writes a 10-character mode string plus null terminator.

Control flow: no runtime logic.

State and persistence behavior: no state. It encodes the caller buffer-size contract for `permstring.c`.

Dependencies/integration: included through `rsync.h` and direct callers that format file modes.

Risks/test signals: callers that allocate fewer than 11 bytes will overflow. Static analysis or compile-time helper usage should prefer `PERMSTRING_SIZE`.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/permstring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/pool_alloc.c -->
# sources/sync-backup/rsync/lib/pool_alloc.c

Purpose: implements rsync's extent-based memory pool allocator for many small, same-lifetime allocations such as file-list data.

Important APIs/types/functions: `pool_create`, `pool_destroy`, `pool_alloc`, `pool_free`, `pool_free_old`, `pool_boundary`, and `pool_stats`; internal `struct alloc_pool`, `struct pool_extent`, `POOL_DEF_EXTENT`, `POOL_QALIGN_P2`, `MINALIGN`, `PTR_ADD`, and `PTR_SUB`.

Control flow: `pool_create` validates alignment, applies defaults, adjusts extent layout for `POOL_INTERN`, rounds extent size to allocation quantum, and records flags. `pool_alloc` rounds requested length, creates a new extent when the live extent lacks room, optionally zeroes it, places allocations from the high end of free space downward, updates stats, and calls the bomb callback on failure. `pool_free` records returned bytes, resets the live extent when fully free, frees non-live extents when all bytes become free/bound, or tracks trapped bytes in `bound`. `pool_free_old` frees all extents older than a boundary address and must not be mixed with `pool_free`. `pool_boundary` optionally forces a new extent and returns a marker for later `pool_free_old`. `pool_stats` writes allocator statistics and extent free/bound counts to a file descriptor.

State and persistence behavior: all state is heap-resident in the pool and its extent list. Stats track created/freed extents and bytes/calls allocated/freed. `POOL_CLEAR` zeroes allocations/extents on creation and some frees, but the allocator is not a secure scrubber. Destroying the pool frees all extents.

Dependencies/integration: includes `rsync.h` for allocation macros (`new0`, `new_array`, `new`), integer types, `snprintf`, and `write`. Used by file-list construction (`flist.c`) for efficient allocation.

Risks/test signals: `pool_free` trusts caller-supplied size and address, does not detect double-free precisely, and only frees an extent when accounting reaches the extent size. Mixing `pool_free` and `pool_free_old` is explicitly forbidden. Tests should cover alignment, `POOL_INTERN`/`POOL_PREPEND`, zero-length allocation, oversize allocation/bomb behavior, extent freeing, boundary freeing, stats output, and misuse scenarios under sanitizers.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/pool_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/pool_alloc.h -->
# sources/sync-backup/rsync/lib/pool_alloc.h

Purpose: public interface and flags for rsync's pool allocator.

Important APIs/types/functions: flags `POOL_CLEAR`, `POOL_NO_QALIGN`, `POOL_INTERN`, and `POOL_PREPEND`; opaque `alloc_pool_t`; functions `pool_create`, `pool_destroy`, `pool_alloc`, `pool_free`, `pool_free_old`, `pool_boundary`; convenience macros `pool_talloc` and `pool_tfree`.

Control flow: no implementation logic in the header beyond typed allocation/free macros that multiply element size by count before delegating to the pool implementation.

State and persistence behavior: no header state. The opaque handle points to heap state managed by `pool_alloc.c`.

Dependencies/integration: includes `<stddef.h>` for `size_t`; used by file-list and other allocation-heavy rsync modules.

Risks/test signals: macro multiplication can overflow before `pool_alloc` sees the size, so callers must bound counts. API users must honor the documented lifetime rules, especially not mixing `pool_free` and `pool_free_old`.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/pool_alloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/lib/snprintf.c -->
# sources/sync-backup/rsync/lib/snprintf.c

Purpose: fallback implementation of `snprintf`, `vsnprintf`, `asprintf`, and `vasprintf` for platforms with missing or non-C99-compliant printf functions.

Important APIs/types/functions: conditional `rsync_vsnprintf`, `rsync_snprintf`, `vasprintf`, `asprintf`, parser/formatter `dopr`, `fmtstr`, `fmtint`, `fmtfp`, `dopr_outch`, `new_chunk`, and `add_cnk_list_entry`; structures `pr_chunk` and `pr_chunk_x`; parser state constants `DP_S_*`, flags `DP_F_*`, conversion flags `DP_C_*`, and chunk types `CNK_*`.

Control flow: when fallback is needed, `dopr` first parses the format string into chunks, including positional parameters and `*` width/precision references. It then walks the `va_list` in parameter order, verifies repeated positional references use the same type, stores values in chunks, and finally renders chunks into the output buffer while maintaining C99 return length semantics and null termination. `fmtstr`, `fmtint`, and `fmtfp` handle padding, precision, signs, integer bases, and simple fixed-point floating output. `vasprintf` performs a sizing `vsnprintf(NULL, 0, ...)`, allocates `ret + 1`, and renders again; `asprintf` wraps it with varargs.

State and persistence behavior: parsing chunks and positional lists are heap-allocated per call and freed before return. `asprintf`/`vasprintf` return heap memory owned by the caller. No global runtime state.

Dependencies/integration: driven by configure macros `HAVE_SNPRINTF`, `HAVE_VSNPRINTF`, `HAVE_C99_VSNPRINTF`, `HAVE_ASPRINTF`, and `HAVE_VASPRINTF`; included in rsync portability builds and mapped through macros in `rsync.h` when needed. Test mode can force fallback compilation and compare against system `sprintf`.

Risks/test signals: the fallback is broad but not a complete modern printf: hex float is not implemented, exponent/general formats are treated through fixed `fmtfp`, floating precision is capped at 9 decimals, and positional-parameter validation can reject formats some libcs accept. `%n` writes through caller pointers and must retain standard semantics. Tests should compile with `TEST_SNPRINTF`, compare return values and truncation behavior, cover positional width/precision, `%.*s` overread prevention, size_t/long long, NULL strings, `asprintf` allocation failure, and platforms with only partial libc support.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/lib/snprintf.c -->
