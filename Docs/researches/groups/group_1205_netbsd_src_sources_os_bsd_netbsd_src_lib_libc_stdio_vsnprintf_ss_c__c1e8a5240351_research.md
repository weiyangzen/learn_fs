# Group Research: group_1205_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_stdio_vsnprintf_ss_c__c1e8a5240351

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vsnprintf_ss.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vsnprintf_ss.c

This file implements `vsnprintf_ss`, a scaled-down, standalone `printf(3)` formatter intended for string output without pulling in full `vfprintf` machinery. It supports ordinary text copying, width, precision, left/right adjustment, zero padding, sign handling, alternate form, and integer length modifiers including `h`, `l`, `ll`/`q`, `j`, `t`, and `z`.

Supported conversions include `%c`, `%s`, signed decimal `%d`/`%i`/`%D`, unsigned `%u`/`%U`, octal `%o`/`%O`, hexadecimal `%x`/`%X`, pointer `%p`, `%n`, literal/unknown conversion fallback, and `%%` by the default conversion path. It deliberately has no floating-point implementation despite defining `FPT`.

The implementation writes through a bounded `PUTCHAR` macro and always computes the full would-have-written return length. It rejects `slen > INT_MAX` with `EOVERFLOW`. It NUL-terminates using either the current pointer or, for a full buffer, `sbuf[-1]`; callers therefore depend on the diagnostic precondition that `sbuf` is non-NULL when `slen != 0`, and the code assumes `slen > 0` for the full-buffer branch.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vsnprintf_ss.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vsprintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vsprintf.c

This file implements locale-aware and default-locale `sprintf`/`vsprintf` wrappers. The core routine is `vsprintf_l`, which constructs a synthetic write-only string `FILE`, marks it `__SWR | __SSTR`, points its buffer at the destination string, assigns an effectively unbounded write size of `INT_MAX`, and delegates formatting to `__vfprintf_unlocked_l`.

After formatting, it appends the final NUL byte at `f._p`. `vsprintf` passes `_current_locale()`, while `sprintf_l` and `sprintf` build a `va_list` and call the corresponding `v` form. `_FILEEXT_SETUP` provides the associated extended `FILE` storage. The file also undefines fortified `vsprintf`/`sprintf` names under `_FORTIFY_SOURCE` so the libc definitions remain visible.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vsprintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vsscanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vsscanf.c

This file implements `vsscanf_l` and `vsscanf`. It wraps an input C string in a synthetic read-only `FILE`, points `_bf._base` and `_p` to the string, sets `_bf._size` and `_r` to `strlen(str)`, installs an `eofread` callback that always returns zero, clears the ungetc buffer base, and delegates parsing to `__svfscanf_unlocked_l`.

The function validates `str` and `fmt` with `_DIAGASSERT`. `vsscanf` simply calls `vsscanf_l` with `_current_locale()`. The wrapper is intentionally thin: scanning semantics, conversions, assignment counting, locale handling, and error behavior live in the shared scanner implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vsscanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vswprintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vswprintf.c

This file implements `vswprintf_l` and `vswprintf`. The locale-aware function formats wide output by creating a malloc-backed string `FILE` with `__SWR | __SSTR | __SALC`, calling `__vfwprintf_unlocked_l`, then converting the resulting multibyte buffer back to `wchar_t` with `mbsrtowcs_l`.

It rejects `n == 0` with `EINVAL`, returns `ENOMEM` if the temporary buffer cannot be allocated, preserves `errno` across formatting failures, and treats conversion failure as `EILSEQ`. If the converted output would fill the destination exactly, it forces `s[n - 1] = L'\0'`, sets `EOVERFLOW`, and returns `-1`. The file notes the inefficient double conversion: wide formatting writes multibyte bytes that this wrapper immediately converts back.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vswprintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vswscanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vswscanf.c

This file implements `vswscanf_l` and `vswscanf`. It converts the source wide string to a temporary multibyte string with `wcsrtombs_l`, wraps that buffer in a synthetic read-only `FILE`, initializes the wide I/O extension state with `WCIO_GET`, and delegates parsing to `__vfwscanf_unlocked_l`.

The temporary buffer size is `wcslen(str) * MB_CUR_MAX_L(loc) + 1`; allocation or conversion failure returns `EOF`. Like `vsscanf`, it installs an `eofread` callback and sets `_r`/`_bf._size` to the converted byte length. The code explicitly calls out the conversion round trip: `vswscanf` converts wide input to multibyte even though the shared wide scanner will convert it back internally.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vswscanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vwprintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vwprintf.c

This file provides the variadic-list wide-output wrappers for standard output. `vwprintf_l` calls `vfwprintf_l(stdout, loc, fmt, ap)`, and `vwprintf` calls `vfwprintf(stdout, fmt, ap)`.

All real formatting, locking, buffering, orientation, and locale conversion behavior is delegated to the `vfwprintf` family. This file only supplies the public `stdout` entry points and weak alias for the locale-aware symbol.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vwprintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vwscanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vwscanf.c

This file provides the variadic-list wide-input wrappers for standard input. `vwscanf` delegates to `vfwscanf(stdin, fmt, ap)`, and `vwscanf_l` delegates to `vfwscanf_l(stdin, loc, fmt, ap)`.

It contains no scanner logic of its own. Its role is to expose the standard wide `stdin` entry points and preserve the locale-aware weak alias convention used by the rest of libc stdio.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vwscanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/wbuf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/wbuf.c

This file implements `__swbuf`, the slow path for writing one byte to a `FILE` whose write buffer is full, line-buffered, unbuffered, or otherwise needs setup. It sets byte orientation via `_SET_ORIENTATION(fp, -1)`, forces `_w` to a conservative value so future `putc` calls re-enter the slow path if interrupted, validates writeability with `cantwrite`, and returns `EOF` with `EBADF` on invalid output streams.

The function flushes if the buffer is already full, writes the byte, decrements `_w`, and flushes again if the buffer becomes full or if the stream is line-buffered and the byte is newline. It is central to stdio output buffering behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/wbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/wcio.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/wcio.h

This header defines the per-`FILE` wide-character I/O extension state. `struct wchar_io_data` stores input and output `mbstate_t` conversion states, a minimal SUSv2 one-character `ungetwc` buffer, its occupancy count, and `wcio_mode` for stream orientation.

The macros expose this state through `_EXT(fp)->_wcio`. `_SET_ORIENTATION` sets orientation only if currently unoriented. `WCIO_FREE` resets orientation and clears wide ungetc state, while `WCIO_FREEUB` only clears the ungetwc buffer count. This header is used by wide stdio implementations to maintain conversion and orientation state alongside classic byte-oriented `FILE` fields.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/wcio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/wprintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/wprintf.c

This file implements `wprintf` and `wprintf_l`. Both functions collect variadic arguments with `va_start`, call the appropriate wide formatter on `stdout`, then `va_end` and return the formatter result.

`wprintf` delegates to `vfwprintf(stdout, fmt, ap)`. `wprintf_l` delegates to `vfwprintf_l(stdout, loc, fmt, ap)`. The file contains no formatting mechanics; it is the public variadic wrapper layer for wide-character standard-output printing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/wprintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/wscanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/wscanf.c

This file implements `wscanf` and `wscanf_l`. Each function builds a `va_list`, delegates scanning to `vfwscanf(stdin, fmt, ap)` or `vfwscanf_l(stdin, loc, fmt, ap)`, and returns the scanner result.

The file supplies only the public variadic wrappers for wide-character `stdin` scanning. Parsing, stream locking, conversion, assignment, and error semantics are inherited from the shared `vfwscanf` implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/wscanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/wsetup.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/wsetup.c

This file implements `__swsetup`, the write-setup routine used by output paths before buffered writes. It initializes stdio globally if needed, verifies that the stream is write-capable or read/write, switches a read/write stream from reading to writing by clearing read state and ungetc buffers, and sets `__SWR`.

If no buffer exists, it calls `__smakebuf`. It then initializes `_w` and `_lbfsize` according to buffering mode: line-buffered streams get `_w = 0` and negative `_lbfsize`; unbuffered streams get `_w = 0`; fully buffered streams get `_w = _bf._size`. Failure to establish write mode returns `EOF`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/wsetup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_abs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_abs.c

This is a lint-library stub for `abs`. It includes `<stdlib.h>` and defines `abs(int)` with an unused argument, returning `0`.

The file is public-domain compatibility scaffolding for lint analysis, not the runtime implementation. The real implementation is in `stdlib/abs.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_abs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_div.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_div.c

This is a lint-library stub for `div`. It includes `<stdlib.h>`, defines `div(int, int)`, initializes a zeroed `div_t`, and returns it.

It exists to satisfy lint symbol/type checking and does not implement runtime division behavior. The real implementation is in `stdlib/div.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_div.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_imaxabs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_imaxabs.c

This public-domain lint stub defines `imaxabs(intmax_t)` and returns `0`. It includes `<inttypes.h>` for the `intmax_t` type.

It is only a lint-library placeholder. Runtime absolute-value behavior is implemented by `stdlib/imaxabs.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_imaxabs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_labs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_labs.c

This public-domain lint stub defines `labs(long)` and returns `0`. It includes `<stdlib.h>` and marks the argument unused.

It exists for lint analysis rather than runtime use. The actual `labs` implementation is in `stdlib/labs.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_labs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_ldiv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_ldiv.c

This public-domain lint stub defines `ldiv(long, long)`, creates a zero-initialized `ldiv_t`, and returns it.

It is type-checking scaffolding for lint and not the real division implementation. Runtime behavior is in `stdlib/ldiv.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_ldiv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_llabs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_llabs.c

This lint-library stub defines `llabs(long long int)` and returns `0`. It includes `<stdlib.h>` and is public-domain compatibility scaffolding.

The real long-long absolute-value routine is implemented in `stdlib/llabs.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/Lint_llabs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/Makefile.inc

This makefile fragment enumerates libc `stdlib` sources, architecture-specific include paths, allocator selection, and manual-page links. It adds core sources such as environment handling, random APIs, conversion helpers, sorting/searching, getopt, tsearch, system, and numeric conversion routines.

Allocator selection is conditional: for normal builds with jemalloc enabled it includes an external jemalloc makefile when `HAVE_JEMALLOC > 100`; otherwise it builds in-tree `jemalloc.c` plus `aligned_alloc.c`. If jemalloc is disabled, it builds `malloc.c`.

The file also adds architecture `stdlib/Makefile.inc`, defines manpages and MLINKS for related APIs, generates `strtou.3` from `strtoi.3`, and adjusts lint flags for `strfmon.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/_env.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/_env.c

This file implements shared environment-array infrastructure used by `getenv`, `setenv`, `putenv`, and `unsetenv` style routines. It tracks libc-owned environment variable strings in a red-black tree keyed by allocation address. Each `env_node_t` stores allocation length, a scrub marker, and inline string data.

Key helpers include `__envvarnamelen` for validating names, `__allocenvvar`, `__freeenvvar`, `__canoverwriteenvvar`, `__getenvslot`, `__findenvvar`, and obsolete compatibility `__findenv`. `__scrubenv` marks live libc-owned strings found in `environ`, frees stale owned strings, and handles whether the active environment array is libc-owned.

Under `_REENTRANT`, read/write locking is provided by `__readlockenv`, `__writelockenv`, and `__unlockenv`. Array growth uses `reallocarr` and rounds capacity up from a minimum of 16.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/_env.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/_rand48.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/_rand48.c

This file defines the shared state and core transition function for the `rand48` family. It initializes global seed, multiplier, and addend arrays from `rand48.h` constants.

`__dorand48` performs the 48-bit linear congruential update on a three-element 16-bit seed array. It multiplies the current seed by the global multiplier, adds the global addend, propagates carries across the three 16-bit words, and writes the updated seed back in place. Public `drand48`, `erand48`, `lrand48`, `jrand48`, and related routines build their return values on top of this transition.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/_rand48.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/a64l.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/a64l.c

This file implements `a64l`, converting up to six base-64-like characters into a `long`. The digit alphabet is the traditional `.` `/` `0-9` `A-Z` `a-z` mapping, each input character contributing six bits at increasing shifts.

The function asserts a non-NULL string, stops at NUL or after six characters, accumulates into `value`, and returns it. It does not reject characters outside the expected ranges; by the historical interface, character ordering drives the mapping.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/a64l.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/abort.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/abort.c

This file implements `abort`. It unblocks `SIGABRT` while blocking other signals, runs stdio cleanup once via the global `__cleanup` hook, raises `SIGABRT`, then resets `SIGABRT` to default and raises it again if the handler returned or the signal was ignored. As a final fallback it calls `_exit(1)`.

The static `aborting` flag prevents recursive cleanup if `abort` is called from a `SIGABRT` handler. The function intentionally ignores signal-mask and handler setup errors because `abort` must not return.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/abort.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/abs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/abs.c

This file implements the standard `abs(int)` function. It returns `-j` when `j < 0`, otherwise `j`.

The implementation is intentionally minimal and follows the historical libc style. It does not special-case the most-negative integer; as in C, negating that value is outside the representable positive range for two's-complement `int`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/abs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/aligned_alloc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/aligned_alloc.c

This file implements C11 `aligned_alloc` in terms of `posix_memalign`. It validates that `alignment` is a nonzero power of two, returning `NULL` with `EINVAL` otherwise. It then raises small valid alignments until they satisfy `posix_memalign`'s minimum `sizeof(void *)` alignment requirement.

The allocation result is returned directly on success. On `posix_memalign` failure, it copies the returned error code to `errno` and returns `NULL`. This implementation does not enforce the C11 rule that `size` be a multiple of `alignment`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/aligned_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/atexit.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/atexit.c

This file implements process-exit and C++ ABI destructor registration. It stores handlers in a LIFO stack of `struct atexit_handler`, with a static pool of 35 entries for normal `atexit` handlers and dynamic allocation for overflow or `__cxa_atexit` DSO-bound handlers.

`__libc_atexit_init` initializes a recursive mutex, needed because finalization can recurse through dynamic-loader cleanup. `__cxa_atexit_internal` registers handlers, `atexit` wraps it for plain void handlers, and ARM EABI gets `__aeabi_atexit`.

`__cxa_finalize` runs matching handlers in reverse registration order, supports `dso == NULL` for full process exit, handles recursive invocation with `call_depth`, restarts if handlers register new handlers, and frees dynamically allocated dead handlers after the outermost finalize completes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/atexit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/atof.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/atof.c

This file implements `atof`. It asserts that the input pointer is non-NULL and returns `strtod(ascii, NULL)`.

All parsing, locale behavior, overflow handling, and error semantics are delegated to `strtod`; `atof` intentionally exposes the historical simplified interface with no end-pointer or reliable error reporting.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/atof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/atoi.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/atoi.c

This file implements `atoi`. It asserts the input string is non-NULL and returns `(int)strtol(str, NULL, 10)`.

The file contains no independent parser. Range handling and conversion are delegated to `strtol`, while the cast to `int` preserves the traditional `atoi` interface and its weak error-reporting properties.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/atoi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/atol.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/atol.c

This file implements `atol`. It asserts the input string is non-NULL and returns `strtol(str, NULL, 10)`.

The implementation is a thin historical wrapper around `strtol`; it provides no end pointer and no direct way to distinguish conversion errors from legitimate results.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/atol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/atoll.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/atoll.c

This file implements `atoll` when the build environment does not already provide it. Under libc it sets up namespace handling and a weak alias. The actual function returns `strtoll(str, NULL, 10)`.

The file is portable across host-tool builds via `nbtool_config.h` and `HAVE_ATOLL`. As with other `ato*` wrappers, conversion details and range behavior are delegated to the corresponding `strto*` function.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/atoll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/bsearch.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/bsearch.c

This file implements standard binary search over a sorted array. `bsearch` validates key, base, and comparator assumptions with `_DIAGASSERT`, then iteratively probes `base + (lim >> 1) * size`.

If the comparator returns zero, it returns the matching element pointer. If the key compares greater, it advances `base` one element past the probe and decrements `lim`; otherwise it searches the left half. The loop halves `lim` each iteration and returns `NULL` when no match is found. The comment explains the odd/even length behavior in detail.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/bsearch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/cxa_thread_atexit.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/cxa_thread_atexit.c

This file implements thread-local C++ destructor registration support. It defines a TLS singly linked list of `struct cxa_dtor` entries, each holding the destructor, object pointer, and optional DSO symbol. The global hidden `__cxa_thread_atexit_used` flag lets `exit` know whether to run thread-local destructors.

`__cxa_thread_atexit_impl` allocates an entry, increments the DSO reference count through `__dl_cxa_refcount` when applicable, and pushes the entry onto the TLS list. `__cxa_thread_run_atexit` pops entries, runs destructors, decrements DSO reference counts, and frees nodes. A weak alias exposes `__cxa_thread_atexit`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/cxa_thread_atexit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/div.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/div.c

This file implements `div(int, int)`. It computes quotient and remainder with native `/` and `%`, then corrects historical machine behavior if division rounded toward negative infinity instead of zero.

The correction triggers when `num >= 0` but `r.rem < 0`: it increments the quotient and subtracts the denominator from the remainder. The comment explains the ANSI requirement that the quotient truncate toward zero and why older division semantics could produce the wrong sign combination.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/div.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/drand48.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/drand48.c

This file implements `drand48`. It returns `erand48(__rand48_seed)`, using the global `rand48` seed state.

All generator advancement and double construction are delegated to `erand48` and the shared `__dorand48` transition. The file supplies the global-state public entry point and weak alias.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/drand48.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/erand48.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/erand48.c

This file implements the portable `erand48` variant. It asserts a non-NULL three-word seed, advances it with `__dorand48`, and returns a double in `[0, 1)` by combining the three 16-bit seed words with `ldexp` at shifts `-48`, `-32`, and `-16`.

Unlike `drand48`, this interface is seed-array based, so callers can maintain independent generator state. It uses ordinary floating-point arithmetic rather than directly constructing IEEE fields.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/erand48.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/erand48_ieee754.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/erand48_ieee754.c

This file implements an IEEE-754-specific `erand48`. It advances the three-word seed with `__dorand48`, constructs a `union ieee_double_u` with sign 0, exponent bias for the range `[1, 2)`, fills fraction bits from the seed words, and returns the constructed double minus 1.

This avoids the `ldexp` arithmetic used by the portable `erand48.c`. `Makefile.inc` notes that this file is normally used but may be replaced by `erand48.c` on targets where the IEEE layout assumptions are unsuitable.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/erand48_ieee754.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/exit.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/exit.c

This file implements `exit`. In libc builds it first runs thread-local C++ destructors if `__cxa_thread_atexit_used` is set, then calls `__cxa_finalize(NULL)` to run process-wide atexit and DSO finalizers. It then invokes the global `__cleanup` hook if installed, typically flushing stdio, and finally terminates via `_exit(status)`.

The file also defines the global `void (*__cleanup)(void)` hook used by both `exit` and `abort`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/exit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/getenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/getenv.c

This file implements `getenv` and `getenv_r`. Both validate variable names using `__envvarnamelen(name, false)` and use the shared environment read lock before searching with `__findenvvar`.

`getenv` returns the direct pointer into `environ` and cannot be implemented via a shared buffer because repeated calls must not invalidate previous returned environment strings. `getenv_r` copies the value into a caller buffer with `strlcpy`, returning `0` on success and `-1` with `ENOENT` or `ERANGE` on missing values or insufficient space.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/getenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/getopt_long.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/getopt_long.c

This file implements NetBSD `getopt_long` and, for tool builds lacking it, replacement `getopt` globals and behavior. It supports POSIX and GNU-compatible modes controlled by option-string prefixes and `POSIXLY_CORRECT`: argument permutation, in-order non-option returns, stopping at non-options, and `--` termination.

`getopt_internal` parses short options, handles required and optional arguments, implements `-W` long-option dispatch, tracks `place`, `optind`, `optarg`, `optopt`, `optreset`, and permutes skipped non-options through `permute_args`, which uses a GCD cycle algorithm.

`getopt_long` matches long options by exact or unambiguous prefix, handles `--name=value`, required/optional/no-argument cases, reports ambiguity and invalid arguments through `warnx` when enabled, writes `flag` values when requested, and returns either `0` or the option `val`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/getopt_long.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/getsubopt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/getsubopt.c

This file implements `getsubopt`, parsing comma- or whitespace-separated suboptions from a mutable option string. It exposes global `suboptarg`, pointing to the token that was parsed and possibly failed to match.

The function skips leading commas and whitespace, isolates the next token in place by inserting NUL terminators, optionally returns a value following `=`, advances `*optionp` to the next token, and searches the caller-provided token array. It returns the matching token index or `-1` if no token matches or no option is available.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/getsubopt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/hcreate.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/hcreate.c

This file implements SysV/XPG hash table APIs: `hcreate`, `hcreate_r`, `hdestroy`, `hdestroy_r`, `hdestroy1`, `hdestroy1_r`, `hsearch`, and `hsearch_r`. A non-reentrant static `htable` backs the classic interface, while `_r` functions operate on caller-supplied `struct hsearch_data`.

Tables are arrays of singly linked bucket heads sized to a power of two between `MIN_BUCKETS` and `MAX_BUCKETS`. Hashing uses the external `__default_hash`; bucket selection masks by `head->size - 1`. `hsearch_r` returns existing entries, reports missing `FIND` with `ESRCH` but a successful API return, and allocates `internal_entry` nodes for `ENTER`. Destroy helpers can optionally free keys and data.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/hcreate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/imaxabs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/imaxabs.c

This file implements `imaxabs`. It returns `-i` when the `intmax_t` argument is negative, otherwise returns the argument unchanged. It also provides a weak alias under libc namespace handling.

The implementation is the direct `intmax_t` analogue of `abs`, with the same representability caveat for the most-negative value.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/imaxabs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/imaxdiv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/imaxdiv.c

This file implements `imaxdiv(intmax_t, intmax_t)`. It computes quotient and remainder with native arithmetic and applies the same truncation-toward-zero correction used by `div.c` if a platform's division semantics produce a negative remainder for a nonnegative numerator.

The result is returned in an `imaxdiv_t`. The file includes namespace handling and a weak alias for libc symbol management.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/imaxdiv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/insque.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/insque.c

This file implements `insque`, inserting an element into a historical doubly linked queue layout. It treats both `entry` and `pred` as `struct qelem` with forward and backward pointers.

The inserted entry's back pointer is set to `pred`. If `pred` is non-NULL, the entry is inserted after it and the old successor's back pointer is updated. If `pred` is NULL, the entry becomes an isolated head with `q_forw = NULL`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/insque.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/jemalloc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/jemalloc.c

This file is NetBSD's older in-tree jemalloc-derived allocator. It implements scalable malloc-family allocation with multiple per-CPU arenas, chunk/run/bin metadata, red-black trees for arena chunks and huge allocations, mmap-backed chunk allocation, optional `sbrk`/`brk` use on selected architectures, internal base allocation, runtime `MALLOC_OPTIONS`, ktrace `utrace`, and fork lock hooks.

Allocation categories are small, large, and huge. Small allocations use size-class bins and bitmap-managed runs. Large allocations use dedicated page runs inside arena chunks. Huge allocations use one or more whole chunks and are tracked in a global `huge` red-black tree. Arena chunks maintain page maps with free-run coalescing metadata and are cached through one spare chunk per arena unless hinting disables it.

Initialization (`malloc_init_hard`) discovers CPU count and page size, reads options from `/etc/malloc.conf`, `MALLOC_OPTIONS`, and `_malloc_options`, computes quantum, small, and chunk settings, initializes global trees/mutexes/base allocation, creates the arenas array, and initializes arena zero. Public APIs include `malloc`, `posix_memalign`, `calloc`, `realloc`, `free`, and `malloc_usable_size`. Internal APIs include `imalloc`, `ipalloc`, `icalloc`, `iralloc`, `idalloc`, and `_malloc_prefork`/postfork variants.

Important behavioral options include abort-on-error, junk fill, `MADV_FREE` hinting, statistics printing, utrace, SysV zero-size semantics, xmalloc abort-on-OOM, and zero-fill. Overflow checks appear in `calloc`, aligned allocation, huge allocation sizing, and chunk rounding paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/jemalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/jrand48.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/jrand48.c

This file implements `jrand48`, the seed-array signed long variant of the `rand48` family. It asserts the seed pointer is non-NULL, advances it with `__dorand48`, and returns a signed 32-bit-style result composed from the high two seed words: `(int16_t)xseed[2] * 65536 + xseed[1]`.

The function mutates caller-provided generator state rather than the global `__rand48_seed`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/jrand48.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/l64a.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/l64a.c

This file implements `l64a` and `l64a_r`, converting a `long` to the traditional base-64-like alphabet used by `a64l`. `l64a` uses a static 8-byte buffer and calls `l64a_r`.

`l64a_r` writes characters for successive six-bit chunks using the `.` `/` `0-9` `A-Z` `a-z` mapping, stops when the unsigned value becomes zero or the buffer has only room for NUL, terminates the string, and returns `0` if the whole value was encoded or `-1` if the buffer was too small.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/l64a.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/labs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/labs.c

This file implements `labs(long)`. It returns `-j` when the argument is negative and `j` otherwise.

It is the long-integer counterpart to `abs.c`, with no additional error handling or special casing for the most-negative representable `long`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/labs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/lcong48.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/lcong48.c

This file implements `lcong48`, which replaces the global `rand48` generator parameters. It expects a seven-element `unsigned short` array: the first three words become `__rand48_seed`, the next three become `__rand48_mult`, and the final word becomes `__rand48_add`.

The function asserts a non-NULL parameter pointer and performs direct assignment. It affects global-state functions such as `drand48`, `lrand48`, and related routines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/lcong48.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/ldiv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/ldiv.c

This file implements `ldiv(long, long)`. It computes native quotient and remainder, then applies the same correction as `div.c` for systems whose signed division rounds toward negative infinity.

The correction ensures the result follows the C requirement for truncation toward zero: if `num >= 0` and the computed remainder is negative, increment the quotient and subtract the denominator from the remainder.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/ldiv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/llabs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/llabs.c

This file implements `llabs(long long int)`. It returns the negated argument when negative, otherwise the argument unchanged. Under libc namespace handling it provides a weak alias for `_llabs`.

It is the long-long counterpart to `abs` and `labs`, with the same normal C overflow caveat for the most-negative value.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/llabs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/lldiv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/lldiv.c

This file implements `lldiv(long long int, long long int)`. It computes quotient and remainder, then applies the historical division-semantics correction from `div.c` to ensure truncation toward zero when needed.

The result is returned as `lldiv_t`. The file includes namespace handling and a weak alias for the libc internal symbol.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/lldiv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/local.h

This local header declares private environment-handling helpers shared by `stdlib` environment routines. It includes `<sys/types.h>` and `<stdbool.h>` and declares `__envvarnamelen`, `__freeenvvar`, `__allocenvvar`, and `__canoverwriteenvvar`.

The declarations expose validation and libc-owned environment allocation management implemented in `_env.c` to related files such as `getenv`, `setenv`, `putenv`, and `unsetenv`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/local.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/lrand48.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/lrand48.c

This file implements `lrand48`, the global-state nonnegative long variant of the `rand48` family. It advances `__rand48_seed` with `__dorand48` and returns a 31-bit value formed from the high seed words: `__rand48_seed[2] * 32768 + (__rand48_seed[1] >> 1)`.

It uses shared global generator state and therefore is affected by `srand48`, `seed48`, and `lcong48`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/lrand48.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/lsearch.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/lsearch.c

This file implements `lsearch` and `lfind` using a shared `linear_base` helper. Both linearly scan `*nelp` elements of width `width`, calling the comparator until a match is found.

`lfind` returns `NULL` on no match. `lsearch` appends the key to the end of the table when no match is found, increments `*nelp`, copies the key with `memcpy`, and returns the inserted element pointer. The implementation notes that the historical API has no way to know total table capacity, so it cannot reliably report insufficient space.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdlib/lsearch.c -->