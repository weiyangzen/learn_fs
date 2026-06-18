# Group Research: group_1203_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_softfloat_timesoftflo_822d498b70f4

Scope checked against `Docs/research_subset_a.md`; all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every listed source file was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/timesoftfloat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/timesoftfloat.c

Read completely: 2641 lines.

This file is the SoftFloat release 2a timing driver. It defines fixed integer, float32, float64, and conditionally floatx80/float128 input vectors, then measures SoftFloat conversion, arithmetic, remainder, square-root, rounding, and comparison functions by repeatedly calling them for at least one clock-second warmup and reporting kops/s.

Key behavior: command-line parsing accepts one function name or `all`, `all1`, `all2`, plus rounding precision, rounding mode, and tininess options. The `functions[]` metadata table records each operation's arity and whether it should be timed across rounding precision, rounding mode, tininess mode, or reduced-precision tininess variants. `timeFunctionVariety` sets global SoftFloat state such as `float_rounding_mode`, `float_detect_tininess`, and, for extended precision builds, `floatx80_rounding_precision`, then dispatches to the matching timing wrapper.

Important interactions: this is a benchmark/test utility for the SoftFloat implementation included in libc, not normal libc runtime code. It depends on `milieu.h`, `softfloat.h`, optional `FLOATX80`/`FLOAT128` build configuration, and every exported SoftFloat arithmetic primitive.

Security/reliability notes: benchmark accuracy depends on `clock()` resolution, compiler optimization behavior, and the fixed input distributions. The code uses old-style implicit `int main`, global mutable SoftFloat mode variables, and repeated boilerplate wrappers, so it is useful as legacy test infrastructure but not a modern harness.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/timesoftfloat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/unorddf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/unorddf2.c

Read completely: 28 lines.

This file implements the GCC helper `__unorddf2` for double-precision SoftFloat values. It returns true when either operand is unordered, detected by comparing each operand with itself using `float64_eq`.

Important interactions: included through `softfloat-for-gcc.h`, `milieu.h`, and `softfloat.h`; used as compiler runtime support on targets where libc supplies software floating-point helpers.

Security/reliability notes: both self-comparisons are intentionally evaluated so signaling NaNs are observed according to SoftFloat behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/unorddf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/unordsf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/unordsf2.c

Read completely: 28 lines.

This file implements the GCC helper `__unordsf2` for single-precision SoftFloat values. It reports unordered comparison status by evaluating `float32_eq(a, a)` and `float32_eq(b, b)` and inverting the combined ordered result.

Important interactions: provides compiler ABI support for soft-float single comparisons.

Security/reliability notes: the structure preserves signaling-NaN side effects by checking both operands rather than short-circuiting after the first NaN.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/unordsf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/unordtf2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/unordtf2.c

Read completely: 32 lines.

This file conditionally implements `__unordtf2` for quad-precision `float128` values when `FLOAT128` is enabled. Like the other unordered helpers, it compares each operand with itself through `float128_eq` and returns true if either comparison is false.

Important interactions: compiler runtime ABI support for quad-precision soft-float comparisons.

Security/reliability notes: compiled out entirely when `FLOAT128` is not configured; both self-comparisons are preserved for signaling-NaN handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/softfloat/unordtf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/Makefile.inc

Read completely: 15 lines.

This make include adds libc's SSP/FORTIFY checked wrapper sources. `SSP_SRCS` lists checked variants for gets/fgets, memory functions, formatted output, string copy/concat functions, and `ssp_redirect.c`; each source is added to `SRCS` with warning level 4.

Important interactions: installs `ssp.3` and `__builtin_object_size.3` manuals and controls whether these fortified entry points are built into libc.

Security/reliability notes: no runtime logic, but this file is the build switchboard for libc's checked-buffer ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/fgets_chk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/fgets_chk.c

Read completely: 55 lines.

This file implements `__fgets_chk`, the fortified `fgets` wrapper. It bypasses checking when the object size is too large for `int`, otherwise fails if the requested `len` exceeds the destination object size, then calls real `fgets`.

Important interactions: reached from fortified `<ssp/stdio.h>` redirects generated by `__builtin_object_size`.

Security/reliability notes: negative `len` values are left to `fgets`; only nonnegative lengths larger than `slen` trigger `__chk_fail()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/fgets_chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/gets_chk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/gets_chk.c

Read completely: 75 lines.

This file implements `__gets_chk`, a fortified wrapper around legacy `gets` behavior. For bounded objects, it reads into a temporary `malloc(slen + 1)` buffer with `fgets`, strips a trailing newline for length checking, fails if the input would fill or exceed the destination, then copies and terminates the destination.

Important interactions: calls the internal `__gets` fallback when the object size is too large or allocation fails.

Security/reliability notes: this mitigates known object-size overflows but preserves dangerous `gets` compatibility in fallback paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/gets_chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/memcpy_chk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/memcpy_chk.c

Read completely: 54 lines.

This file implements `__memcpy_chk`. It fails when `len > slen`, checks source/destination overlap with `__ssp_overlap`, then delegates to `memcpy`.

Important interactions: backs fortified `memcpy` expansion from SSP headers.

Security/reliability notes: unlike plain `memcpy`, this wrapper treats overlap as a checked failure, matching the undefined-overlap contract.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/memcpy_chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/memmove_chk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/memmove_chk.c

Read completely: 50 lines.

This file implements `__memmove_chk`. It only validates that the requested length fits within the destination object size, then calls `memmove`.

Important interactions: fortified `memmove` backend.

Security/reliability notes: overlap is allowed by design, so this wrapper does not call `__ssp_overlap`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/memmove_chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/memset_chk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/memset_chk.c

Read completely: 49 lines.

This file implements `__memset_chk`. It checks `len > slen` and calls `__chk_fail()` on overflow, otherwise delegates to `memset`.

Important interactions: fortified `memset` backend.

Security/reliability notes: the only policy is destination-size enforcement; value and pointer validity remain normal `memset` responsibilities.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/memset_chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/snprintf_chk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/snprintf_chk.c

Read completely: 59 lines.

This file implements `__snprintf_chk`. It fails if the caller-requested output limit exceeds the known destination object size, then forwards variadic arguments to `vsnprintf`.

Important interactions: fortified `snprintf` wrapper; the `flags` parameter is accepted for ABI compatibility but unused.

Security/reliability notes: the wrapper prevents an oversized explicit bound but leaves format-string correctness to `vsnprintf`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/snprintf_chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/sprintf_chk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/sprintf_chk.c

Read completely: 63 lines.

This file implements `__sprintf_chk`. If the destination object size is representable as an `int`, it formats through `vsnprintf` using `slen` and fails when the formatted length would not fit; otherwise it falls back to `vsprintf`.

Important interactions: fortified `sprintf` backend.

Security/reliability notes: the large-object fallback preserves unbounded `sprintf` behavior, which is compatibility-oriented rather than strictly safe.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/sprintf_chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/ssp_redirect.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/ssp_redirect.c

Read completely: 56 lines.

This file forces definitions of selected SSP redirect functions into libc by compiling with `_FORTIFY_SOURCE 2` and `__ssp_inline`. A static `__used` function references fortified forms of `getcwd`, `read`, and `readlink` through harmless calls.

Important interactions: ensures redirect symbols required by fortified headers are emitted in libc.

Security/reliability notes: runtime use is not intended; its value is link-time symbol materialization.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/ssp_redirect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/stpcpy_chk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/stpcpy_chk.c

Read completely: 58 lines.

This file implements `__stpcpy_chk`. It computes `strlen(src)`, fails if the string plus terminator cannot fit in `slen`, rejects overlap, copies with `memcpy`, and returns the pointer to the copied terminator position.

Important interactions: fortified `stpcpy` backend, with a compatibility declaration for older GCC.

Security/reliability notes: it checks overlap only across `len` bytes, while copying `len + 1`; the size check still protects the terminator from overflowing the destination.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/stpcpy_chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/stpncpy_chk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/stpncpy_chk.c

Read completely: 56 lines.

This file implements `__stpncpy_chk`. It fails if `len` exceeds the destination object size, rejects overlap for the specified range, and delegates to `stpncpy`.

Important interactions: fortified `stpncpy` backend.

Security/reliability notes: behavior follows bounded-copy semantics, including possible non-NUL-terminated output.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/stpncpy_chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/strcat_chk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/strcat_chk.c

Read completely: 62 lines.

This file implements `__strcat_chk` by manually walking the destination and source while decrementing the known destination capacity. It fails if the existing destination string, appended source, or final terminator would exceed `slen`.

Important interactions: fortified `strcat` backend.

Security/reliability notes: no explicit overlap detection is performed; overflow detection is capacity-driven.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/strcat_chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/strcpy_chk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/strcpy_chk.c

Read completely: 55 lines.

This file implements `__strcpy_chk`. It computes `strlen(src) + 1`, fails if that exceeds the destination object size, rejects overlap, and copies the full string with `memcpy`.

Important interactions: fortified `strcpy` backend.

Security/reliability notes: source must still be a valid NUL-terminated string; the wrapper protects only known destination bounds and overlap.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/strcpy_chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/strncat_chk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/strncat_chk.c

Read completely: 73 lines.

This file implements `__strncat_chk`. It returns immediately for zero append length, fails if the requested append bound exceeds `slen`, scans the existing destination within capacity, copies at most `len` source bytes, and ensures final NUL termination fits.

Important interactions: fortified `strncat` backend.

Security/reliability notes: the initial `len > slen` check is conservative but the full safety check is the later capacity countdown over existing and appended bytes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/strncat_chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/strncpy_chk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/strncpy_chk.c

Read completely: 55 lines.

This file implements `__strncpy_chk`. It validates `len <= slen`, rejects overlap for the requested range, and delegates to `strncpy`.

Important interactions: fortified `strncpy` backend.

Security/reliability notes: preserves `strncpy` semantics, including padding and possible lack of NUL termination.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/strncpy_chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/vsnprintf_chk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/vsnprintf_chk.c

Read completely: 51 lines.

This file implements `__vsnprintf_chk`. It fails if the requested output limit is larger than the known object size, then calls `vsnprintf`.

Important interactions: fortified `vsnprintf` backend.

Security/reliability notes: `flags` is unused; the wrapper checks buffer extent but not format-string safety.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/vsnprintf_chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/vsprintf_chk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/vsprintf_chk.c

Read completely: 60 lines.

This file implements `__vsprintf_chk`. For object sizes within `INT_MAX`, it formats through `vsnprintf` and fails if the resulting length reaches or exceeds `slen`; for larger sizes it calls `vsprintf`.

Important interactions: fortified `vsprintf` backend.

Security/reliability notes: large-object fallback keeps traditional unbounded behavior for ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/ssp/vsprintf_chk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/Makefile.inc

Read completely: 78 lines.

This make include adds the NetBSD libc stdio implementation sources and associated manuals. It lists core byte and wide I/O files, memory-stream files, formatted I/O, scanf/printf locale variants, temporary-file helpers, and compatibility exclusions under `AUDIT`.

Important interactions: controls which stdio objects are built into libc and installs extensive manpage links for related APIs.

Security/reliability notes: no runtime logic, but build inclusion here defines the exported stdio surface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/clrerr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/clrerr.c

Read completely: 58 lines.

This file implements the function form of `clearerr`. It locks the stream, calls the internal `__sclearerr(fp)`, and unlocks.

Important interactions: uses `reentrant.h` locking and `local.h` stdio internals.

Security/reliability notes: assumes a non-NULL `FILE *`; diagnostics use `_DIAGASSERT`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/clrerr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/dprintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/dprintf.c

Read completely: 73 lines.

This file implements `dprintf` and `dprintf_l`. Both collect variadic arguments and delegate to `vdprintf` or `vdprintf_l`.

Important interactions: `dprintf_l` has a weak alias for locale namespace handling.

Security/reliability notes: all formatting and descriptor write behavior lives in the delegated `vdprintf` implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/dprintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fclose.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fclose.c

Read completely: 77 lines.

This file implements `fclose`. It rejects already-free streams with `EBADF`, locks the stream, frees wide I/O state, flushes pending writes, calls the stream close hook, frees allocated buffers/ungetc/line buffers, unlocks, and marks the `FILE` slot reusable.

Important interactions: depends on `__sflush`, stream operation hooks, `WCIO_FREE`, `FREEUB`, and `FREELB`.

Security/reliability notes: after close it deliberately poisons `_file`, `_flags`, `_r`, and `_w` to reduce accidental reuse.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fclose.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fdopen.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fdopen.c

Read completely: 123 lines.

This file implements `fdopen`. It parses mode flags, verifies the descriptor fits in the `FILE` short `_file` field, checks that requested access is compatible with `fcntl(F_GETFL)`, optionally enforces regular-file mode, allocates a `FILE`, and installs standard read/write/seek/close hooks.

Important interactions: uses `__sflags`, `__sfp`, `__sread`, `__swrite`, `__sseek`, and `__sclose`.

Security/reliability notes: handles append mode specially when the underlying descriptor lacks `O_APPEND`, and fails descriptors at or above `USHRT_MAX`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fdopen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/feof.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/feof.c

Read completely: 65 lines.

This file implements the function form of `feof`. It locks the stream, reads EOF status via `__sfeof(fp)`, unlocks, and returns the result.

Important interactions: wrapper around the macro/internal status bit.

Security/reliability notes: no side effects beyond locking.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/feof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/ferror.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/ferror.c

Read completely: 65 lines.

This file implements the function form of `ferror`. It locks the stream, reads error status through `__sferror(fp)`, unlocks, and returns it.

Important interactions: simple public wrapper over stdio internal flags.

Security/reliability notes: assumes valid `FILE *`; no error recovery is attempted.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/ferror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fflush.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fflush.c

Read completely: 120 lines.

This file implements `fflush` and internal `__sflush`. `fflush(NULL)` walks all open streams under `__sfp_lock`; single-stream flush validates write-capable state, then `__sflush` writes buffered bytes through the stream write hook and optionally calls a stream flush hook.

Important interactions: used by close, seek, cleanup, and write paths; `_fwalk(__sflush)` handles process-wide flushing.

Security/reliability notes: write failures set `__SERR` and return `EOF`; buffers are reset before invoking the write hook to tolerate longjmp or buffer replacement.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fflush.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetc.c

Read completely: 61 lines.

This file implements `fgetc`. It locks the stream, calls `__sgetc(fp)`, unlocks, and returns the byte or EOF.

Important interactions: function wrapper for macro-style stdio byte input.

Security/reliability notes: refill and error handling are delegated to the internal `__sgetc` path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetln.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetln.c

Read completely: 64 lines.

This file implements `fgetln` by locking the stream and calling `__fgetstr(fp, lenp, '\n')`. The implementation now uses the shared `getdelim`-based helper, returning a NUL-terminated internal buffer while preserving `fgetln` length reporting.

Important interactions: weak alias `_fgetln`; depends on `fgetstr.c`.

Security/reliability notes: returned storage is stream-owned and overwritten by later line reads.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetln.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetpos.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetpos.c

Read completely: 67 lines.

This file implements `fgetpos`. It captures relevant wide-character conversion state from the stream extension when wide mode is active, then stores the byte offset returned by `ftello`.

Important interactions: pairs with `fsetpos` and depends on `WCIO_GET` and `ftello`.

Security/reliability notes: returns nonzero when `ftello` fails; wide-state preservation is tied to stream read/write hook presence.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetpos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fgets.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fgets.c

Read completely: 131 lines.

This file implements `fgets`. It locks the stream, sets byte orientation, refills as needed, copies from the internal read buffer up to newline or `n - 1`, NUL-terminates, and returns `NULL` only when no bytes were read or the length is invalid.

Important interactions: depends on `__srefill`, stream buffer fields, and `memchr`/`memcpy`.

Security/reliability notes: `n <= 0` is treated as `EINVAL` and sets stream error; partial lines at EOF are returned.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fgets.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetstr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetstr.c

Read completely: 66 lines.

This file implements internal `__fgetstr`, the shared line/string reader for `fgetln`. It calls `__getdelim` on the stream extension's reusable `_fgetstr_buf` and `_fgetstr_len`, reports the byte count, and fixes `EOVERFLOW` to `EINVAL` for `fgetln` compatibility.

Important interactions: uses `_EXT(fp)` storage from `fileext.h`.

Security/reliability notes: returned memory is owned by the stream extension and reused.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetwc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetwc.c

Read completely: 102 lines.

This file implements `fgetwc` and unlocked internal `__fgetwc_unlock`. It sets wide orientation, returns pending `ungetwc` characters first, refills byte buffers as needed, converts bytes with `mbrtowc`, maintains input conversion state, and advances stream pointers.

Important interactions: used by wide line/string input and depends on `WCIO_GET`, `__srefill`, and locale multibyte conversion state.

Security/reliability notes: invalid multibyte input sets `__SERR`; incomplete sequences consume current buffered bytes and retry after refill.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetwc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetwln.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetwln.c

Read completely: 120 lines.

This file implements `fgetwln`, a wide-character analogue of `fgetln`. It locks the stream, sets wide orientation, reads with `__fgetwc_unlock` until newline or WEOF, grows the stream extension line buffer in 512-wide-character chunks, and returns the buffer with a length count.

Important interactions: reuses `_EXT(fp)->_fgetstr_buf` as wide storage and depends on `__fgetwc_unlock`.

Security/reliability notes: allocation failure sets `__SERR`; returned buffer is not necessarily NUL-terminated and is stream-owned.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetwln.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetws.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetws.c

Read completely: 88 lines.

This file implements `fgetws`. It validates positive length, sets wide orientation, reads wide characters one at a time with `__fgetwc_unlock`, stops at newline, EOF after some data, or capacity, then NUL-terminates.

Important interactions: wide string input wrapper around the lower-level wide character reader.

Security/reliability notes: `n <= 0` returns `NULL` with `EINVAL`; errors and EOF before any character also return `NULL`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetws.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fileext.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fileext.h

Read completely: 74 lines.

This private header defines `struct __sfileext`, the extension storage attached to each `FILE`. It contains ungetc storage, wide-character I/O state, reusable `fgetstr` buffer state, and, in reentrant builds, mutex/condition/owner/count/cancellation fields for stream locking.

Important interactions: `_EXT`, `_UB`, lock macros, and `_FILEEXT_SETUP` are used throughout stdio allocation, locking, ungetc, and wide I/O.

Security/reliability notes: correct initialization through `_FILEEXT_SETUP` is required before stream locks or extension buffers are used.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fileext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fileno.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fileno.c

Read completely: 70 lines.

This file implements `_fileno` and weak aliases `fileno` to it. It locks the stream, returns `__sfileno(fp)`, and unlocks.

Important interactions: public function form of the descriptor macro.

Security/reliability notes: descriptor validity behavior is delegated to `__sfileno`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fileno.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/findfp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/findfp.c

Read completely: 228 lines.

This file owns stdio stream allocation and initialization. It defines the standard `__sF[3]` streams, extension objects, the initial static `usual` stream pool, the glue-list allocator `moreglue`, `__sfpinit`, `__sfp`, `f_prealloc`, `_cleanup`, and `__sinit`.

Important interactions: every `fopen`-style function obtains a `FILE` via `__sfp`; `_cleanup` flushes all streams on process exit; `_fwalk` traverses the glue list.

Security/reliability notes: stream allocation is protected by `__sfp_lock` in reentrant builds. `f_prealloc` can allocate many `FILE` slots based on `_SC_OPEN_MAX`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/findfp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/flags.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/flags.c

Read completely: 122 lines.

This file implements `__sflags`, translating stdio mode strings into internal `FILE` flags and `open(2)` flags. It supports `r`, `w`, `a`, `+`, `b`, and NetBSD extensions `e` for close-on-exec, `f` for regular-file-only, `l` for no symlink following, and `x` for exclusive creation.

Important interactions: used by `fopen`, `fdopen`, `freopen`, and `fmemopen`.

Security/reliability notes: invalid leading mode returns `EINVAL`; unknown trailing mode characters are ignored for compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/flags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/floatio.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/floatio.h

Read completely: 55 lines.

This private header defines buffer sizing constants for floating-point scanf/printf conversion: `MAXEXP`, `MAXFRACT`, and `MAXEXPDIG`. It includes a compile-time check that `LDBL_MAX_EXP` remains within the assumed exponent digit budget.

Important interactions: used by formatted I/O conversion code outside this group.

Security/reliability notes: correctness depends on these constants being large enough for all supported long-double formats.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/floatio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/flockfile.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/flockfile.c

Read completely: 183 lines.

This file implements `flockfile`, `ftrylockfile`, `funlockfile`, and internal lock/unlock helpers. In reentrant builds it tracks recursive ownership, waits on a condition variable, and disables cancellation around internal locks; non-reentrant builds are no-ops.

Important interactions: all stdio functions use the locking state defined in `fileext.h`.

Security/reliability notes: assumes `thr_t` behaves as a pointer-like value. Internal lock cancellation-state handling is delicate because condition waits are cancellation points.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/flockfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fmemopen.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fmemopen.c

Read completely: 240 lines.

This file implements `fmemopen` using a custom cookie with `head`, `tail`, current position, and end-of-buffer pointers. It provides memory read, write, seek, and close hooks, allocates backing storage when `buf == NULL` for read-write modes, initializes append/truncate behavior, and returns a `FILE` from `__sfp`.

Important interactions: uses `__sflags` and stdio custom-cookie hook fields.

Security/reliability notes: size zero and read/write modes without caller storage are invalid. Writes always maintain a NUL terminator when possible and stop before overflowing the memory region.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fmemopen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fopen.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fopen.c

Read completely: 104 lines.

This file implements `fopen`. It parses mode flags, allocates a `FILE`, opens the path with `open`, rejects descriptors too large for `_file`, installs normal file operation hooks, and seeks to end for append mode so `ftell` starts correctly.

Important interactions: uses `__sflags`, `__sfp`, `__sread`, `__swrite`, `__sseek`, and `__sclose`.

Security/reliability notes: open failures release the reserved stream slot; descriptor width is explicitly guarded.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fopen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fparseln.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fparseln.c

Read completely: 249 lines.

This file implements `fparseln` when the host lacks a usable version. It reads logical lines, handles escaped comment characters, removes trailing newlines, processes line continuations, optionally unescapes selected escape sequences, tracks line numbers, and returns a newly allocated NUL-terminated buffer.

Important interactions: uses `fgetln` or `__fgetstr` depending on reentrant/tool build configuration.

Security/reliability notes: allocation failures free partial buffers and return `NULL`; callers own the returned buffer. Escape handling is byte-oriented and controlled by caller-supplied `str[3]` and flags.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fparseln.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fprintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fprintf.c

Read completely: 74 lines.

This file implements `fprintf` and `fprintf_l`. Both gather variadic arguments and delegate to `vfprintf` or `vfprintf_l`.

Important interactions: locale variant has weak alias namespace handling.

Security/reliability notes: format parsing and writes are entirely delegated to the vfprintf layer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fprintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fpurge.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fpurge.c

Read completely: 75 lines.

This file implements `fpurge`, which discards buffered input/output without writing it. It rejects unopened streams, frees ungetc and wide I/O state, resets buffer pointers and counters, and preserves line/unbuffered write sizing rules.

Important interactions: manipulates core `FILE` buffering fields directly.

Security/reliability notes: unlike `fflush`, pending output is dropped; this is an intentional nonstandard behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fpurge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fputc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fputc.c

Read completely: 59 lines.

This file implements `fputc`. It locks the stream, writes one character through `__sputc`, unlocks, and returns the result.

Important interactions: function wrapper for the byte-output macro path.

Security/reliability notes: buffering and errors are delegated to `__sputc`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fputc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fputs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fputs.c

Read completely: 76 lines.

This file implements `fputs`. It builds a one-element `__suio`/`__siov` around the string, treats a NULL argument as `"(null)"`, locks the stream, sets byte orientation, and writes through `__sfvwrite`.

Important interactions: shares the vector write engine in `fvwrite.c`.

Security/reliability notes: accepting NULL as `"(null)"` is a compatibility extension, not ISO C behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fputs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fputwc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fputwc.c

Read completely: 100 lines.

This file implements `fputwc` and `__fputwc_unlock`. It sets wide orientation, resets pending ungetwc state, converts one wide character to multibyte with `wcrtomb`, and writes the resulting bytes through `__sfvwrite`.

Important interactions: used by `fputws` and wide output paths.

Security/reliability notes: conversion failure returns WEOF with `EILSEQ`; missing wide I/O state returns WEOF with `ENOMEM`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fputwc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fputws.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fputws.c

Read completely: 63 lines.

This file implements `fputws`. It locks the stream, sets wide orientation, writes each wide character via `__fputwc_unlock`, and returns `-1` on the first WEOF.

Important interactions: simple loop over the wide-character output primitive.

Security/reliability notes: stops at the first NUL wide character and does not append a newline.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fputws.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fread.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fread.c

Read completely: 141 lines.

This file implements `fread`. It detects `size * count` overflow, returns zero for zero-sized reads, locks the stream, handles unbuffered streams by reading directly into the caller buffer, otherwise drains internal buffers and refills with `__srefill`.

Important interactions: core buffered input path for binary reads.

Security/reliability notes: overflow sets `EOVERFLOW` and stream error. Partial reads return complete item count only.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/freopen.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/freopen.c

Read completely: 188 lines.

This file implements `freopen`. It parses new mode flags, flushes and closes the old stream as required, opens the replacement path, tries to preserve the original descriptor with `dup2`, releases old buffers/ungetc/wide state, installs normal file hooks, and seeks to end for append mode.

Important interactions: shares flag parsing and standard file hooks with `fopen`.

Security/reliability notes: tries a second open after closing the old descriptor on `ENFILE`/`EMFILE`; if reopening fails, the original stream slot is freed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/freopen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fscanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fscanf.c

Read completely: 78 lines.

This file implements `fscanf` and `fscanf_l`. Both collect variadic arguments and call `__svfscanf` or `__svfscanf_l`.

Important interactions: thin public wrappers around the scanf engine.

Security/reliability notes: format parsing, locale behavior, and input error handling are delegated.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fscanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fseek.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fseek.c

Read completely: 66 lines.

This file implements `fseek` as a `long` offset wrapper around `fseeko`. It converts the input offset to `off_t` and delegates all logic.

Important interactions: legacy API shim over the large-file-aware seek implementation.

Security/reliability notes: a commented-out unsigned `SEEK_SET` conversion documents an intentionally rejected compatibility behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fseek.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fseeko.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fseeko.c

Read completely: 276 lines.

This file implements `fseeko`, the main stdio seek engine. It validates seekability and offsets, converts `SEEK_CUR` into absolute positions accounting for buffered read/write and ungetc data, attempts optimized seeks within or near the current read buffer for regular files, and falls back to flushing plus calling the stream seek hook.

Important interactions: used by `fseek`, `fsetpos`, and code that needs large offsets.

Security/reliability notes: clears EOF and discards ungetc data on successful seek. Optimization is disabled for write, read-write, unbuffered, or non-regular streams.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fseeko.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fsetpos.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fsetpos.c

Read completely: 70 lines.

This file implements `fsetpos`. It restores saved wide-character conversion state when wide mode is active, then seeks to the stored `fpos_t` byte offset using `fseeko`.

Important interactions: pair for `fgetpos`.

Security/reliability notes: failure behavior is delegated to `fseeko`; invalid `fpos_t` values can fail as invalid seeks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fsetpos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/ftell.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/ftell.c

Read completely: 106 lines.

This file implements `ftell`. It flushes pending writes, obtains the underlying offset from cached `__SOFF` or the seek hook, adjusts for unread buffered and ungetc bytes or unwritten buffered bytes, checks for `long` overflow, and returns the position.

Important interactions: legacy `long` API counterpart to `ftello`.

Security/reliability notes: non-seekable streams fail with `ESPIPE`; offsets too large for `long` fail with `EOVERFLOW`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/ftell.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/ftello.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/ftello.c

Read completely: 101 lines.

This file implements `ftello`. It mirrors `ftell` but returns `off_t`, flushing pending writes, querying current underlying offset, and adjusting for buffered input/output state.

Important interactions: used by `fgetpos`; weak alias `_ftello`.

Security/reliability notes: non-seekable streams fail with `ESPIPE`; no `long` truncation check is needed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/ftello.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/funopen.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/funopen.c

Read completely: 173 lines.

This file implements `funopen2` and compatibility `funopen` for custom stream backends. `funopen2` installs caller-provided read/write/seek/flush/close hooks directly; `funopen` wraps older `int`-sized callbacks in adapters that clamp large transfer sizes and free the adapter cookie on close.

Important interactions: custom-cookie stream creation used by memory and application-defined streams.

Security/reliability notes: `funopen`'s write adapter loops across large writes but relies on callbacks making progress; a zero-byte successful write would be problematic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/funopen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fvwrite.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fvwrite.c

Read completely: 236 lines.

This file implements `__sfvwrite`, the central vector write engine. It validates residual size, checks write capability, and handles unbuffered, fully buffered, string-buffer, auto-growing string, and line-buffered streams, writing directly or copying into the stream buffer as appropriate.

Important interactions: used by `fputs`, `fputwc`, formatted output, and other output helpers.

Security/reliability notes: write failures set `__SERR`. The code caps direct writes at `INT_MAX` and treats string output specially so snprintf-style streams can report required length without necessarily writing all bytes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fvwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fvwrite.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fvwrite.h

Read completely: 50 lines.

This private header defines `struct __siov` and `struct __suio`, the lightweight vector I/O descriptors consumed by `__sfvwrite`, and declares `__sfvwrite`.

Important interactions: included by output functions that batch memory regions into the stdio write engine.

Security/reliability notes: no logic here; callers must keep `uio_resid` consistent with the vector lengths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fvwrite.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fwalk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fwalk.c

Read completely: 66 lines.

This file implements `_fwalk`, iterating every allocated `FILE` in the glue list and OR-ing the return value of a caller-supplied function for streams with nonzero flags.

Important interactions: used by `fflush(NULL)` and cleanup-style operations.

Security/reliability notes: caller is responsible for external locking when walking the global stream list.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fwalk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fwide.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fwide.c

Read completely: 72 lines.

This file implements `fwide`. It normalizes mode to -1, 0, or 1, locks the stream, obtains wide I/O state, sets orientation if it was previously undecided and the requested mode is nonzero, then returns the resulting orientation.

Important interactions: byte and wide I/O functions also set orientation through internal macros.

Security/reliability notes: if `WCIO_GET(fp)` fails, this implementation returns 0 while still inside the locked section, which appears to risk leaving the stream locked.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fwide.c -->