# Group Research: group_1204_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_stdio_fwprintf_c_sour_8847fee467bf

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fwprintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fwprintf.c

Implements `fwprintf()` and `fwprintf_l()` as variadic wide-character formatted-output wrappers. They create a `va_list`, delegate to `vfwprintf()` or `vfwprintf_l()`, then return that result.

This file contains no formatting engine logic. It is the public API adapter for `vfwprintf.c` and defines the weak alias `fwprintf_l -> _fwprintf_l`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fwprintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fwrite.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fwrite.c

Implements `fwrite()` by wrapping the caller buffer in one `__siov`/`__suio` vector and writing through `__sfvwrite()` under `FLOCKFILE()`. On complete success it returns the requested object count; on short/error write it returns only the number of whole objects written.

It detects `size * count` overflow before writing, sets `errno = EOVERFLOW`, marks `__SERR`, and returns zero. A zero `size` or `count` returns zero as required by SUSv2.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fwscanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fwscanf.c

Implements `fwscanf()` and `fwscanf_l()` as variadic wrappers over `vfwscanf()` and `vfwscanf_l()`. It only handles `va_list` setup/teardown.

This is part of the wide scanf public API surface and defines the weak alias `fwscanf_l -> _fwscanf_l`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/fwscanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/getc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/getc.c

Provides function versions of the `getc` and `getc_unlocked` macros. `getc()` locks the stream, calls `__sgetc(fp)`, unlocks, and returns the byte or `EOF`; `getc_unlocked()` calls `__sgetc()` without locking.

It depends on internal stdio fast-path helpers from `local.h` and uses `_DIAGASSERT()` for null-stream diagnostics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/getc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/getchar.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/getchar.c

Provides function versions of `getchar()` and `getchar_unlocked()`. Both read from `stdin` via `__sgetc()`, with only the normal variant locking `stdin`.

This is a minimal adapter around the byte input machinery shared with `getc.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/getchar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/getdelim.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/getdelim.c

Implements internal `__getdelim()` and public `getdelim()`. It reads from a byte-oriented stream until the separator or EOF, grows the caller buffer to powers of two with a 128-byte minimum, copies directly from the stdio buffer, appends NUL, and returns the byte count.

Null `buf`/`buflen` set `EINVAL`; length overflow or exceeding `SSIZE_MAX` sets `EOVERFLOW`; all error exits mark the stream `__SERR`. Public `getdelim()` only adds stream locking.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/getdelim.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/getline.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/getline.c

Implements `getline()` as `getdelim(buf, buflen, '\n', fp)`. It contains no independent line-reading logic.

The file defines the weak alias `getline -> _getline` where supported.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/getline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/gets.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/gets.c

Implements legacy unsafe `gets()` through internal `__gets()`. It locks `stdin`, reads bytes with `getchar_unlocked()` until newline or EOF, NUL-terminates the caller buffer, and returns `NULL` only if EOF occurs before any byte is read.

The file emits a link-time warning that `gets()` is unsafe. There is no bounds check by design, so this exists only for legacy ABI/API compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/gets.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/gettemp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/gettemp.c

Provides the shared `GETTEMP()` implementation behind `mkstemp`, `mkstemps`, `mkostemp`, `mkdtemp`, `mktemp`, `tmpnam`, and `tempnam`. It validates path, suffix length, mutually exclusive create modes, allowed open flags, and `MAXPATHLEN`, then replaces trailing `X` characters with random base-62 characters.

For creation it checks the parent directory, then uses `open(..., O_CREAT|O_EXCL|O_RDWR|oflags, 0600)` or `mkdir(..., 0700)`. For name-only generation it uses `lstat()` and succeeds only if the candidate is absent. Collision handling cycles deterministically through the generated character space using the saved initial random combination.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/gettemp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/gettemp.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/gettemp.h

Internal header for the temporary-name helper family. It maps `GETTEMP` to `__nbcompat_gettemp` for nbtool builds or to libc `__gettemp` otherwise, includes the needed platform headers, and declares `int GETTEMP(char *, int *, int, int, int)`.

This lets the same wrapper files build in both libc and host-tool compatibility contexts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/gettemp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/getw.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/getw.c

Implements historical `getw(FILE *)`. It reads one raw `int` object with `fread()` and returns it on success, otherwise returns `EOF`.

The format is binary and host-endian dependent; the function is compatibility I/O, not portable serialization.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/getw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/getwc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/getwc.c

Provides the function version of the `getwc` macro. It directly returns `fgetwc(fp)`.

Wide decoding, orientation, locking, and error behavior are all delegated to `fgetwc()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/getwc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/getwchar.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/getwchar.c

Provides the function version of `getwchar()`. It reads one wide character from `stdin` by calling `fgetwc(stdin)`.

This is a minimal public wrapper for wide standard-input reads.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/getwchar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/glue.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/glue.h

Defines `struct glue`, the linked-list node used to manage dynamically allocated arrays of `FILE` objects after the initial statically allocated streams. Each node stores the next node, number of `FILE` objects, and pointer to the object array.

It declares global `__sglue`, making this header part of stdio stream-allocation internals.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/glue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/local.h

Central internal header for NetBSD libc stdio. It declares private stream lifecycle, buffer, read/write/seek/close, scanf/printf, wide I/O, getdelim, fgetstr, locking, and cleanup functions.

Important macros include `cantwrite()`, ungetc-buffer detection/freeing (`HASUB`, `FREEUB`), fgetstr buffer cleanup (`FREELB`), and `__long_overflow()`. This is the shared contract between small public wrappers and the larger stdio engines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/local.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/makebuf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/makebuf.c

Implements stdio buffer selection/allocation through `__smakebuf()` and `__swhatbuf()`. `__swhatbuf()` uses `fstat()` to choose a buffer size, determine whether the stream could be a tty, and decide whether seek optimization can be enabled.

`__smakebuf()` honors existing unbuffered flags, `STDBUF`/`STDBUF<fd>` environment overrides, mallocs buffers when possible, enables line buffering for ttys, and falls back to the one-byte internal buffer on allocation failure. Environment syntax supports unbuffered, line-buffered, or fully buffered modes plus an optional size up to 1 MiB.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/makebuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/mkdtemp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/mkdtemp.c

Implements `mkdtemp(char *path)` using `GETTEMP(path, NULL, 1, 0, 0)`. On success it returns the caller path after creating the directory; on failure it returns `NULL`.

The wrapper is conditionally compiled for nbtool compatibility when the host lacks `mkdtemp`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/mkdtemp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/mkostemp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/mkostemp.c

Implements `mkostemp(char *path, int oflags)`. It delegates to `GETTEMP()` with no suffix and file creation enabled, returning the created fd or `-1`.

Validation of allowed `oflags` is centralized in `GETTEMP()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/mkostemp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/mkostemps.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/mkostemps.c

Implements `mkostemps(char *path, int slen, int oflags)`. It delegates to `GETTEMP()` with a caller-specified suffix length and open flags, returning the created fd or `-1`.

It is the suffix-aware variant of `mkostemp()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/mkostemps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/mkstemp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/mkstemp.c

Implements `mkstemp(char *path)` as a safe temporary file creator through `GETTEMP(path, &fd, 0, 0, 0)`. It returns an exclusive-created read/write file descriptor or `-1`.

The file provides a weak alias for `_mkstemp` where enabled and is conditionally compiled for nbtool builds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/mkstemp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/mkstemps.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/mkstemps.c

Implements `mkstemps(char *path, int slen)` using `GETTEMP()` with file creation and a fixed suffix length. It returns the created fd or `-1`.

This is the non-`oflags` suffix-aware temporary file wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/mkstemps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/mktemp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/mktemp.c

Implements internal `_mktemp()` and public `mktemp()` as name-only calls to `GETTEMP(path, NULL, 0, 0, 0)`. Both mutate the template in place and return the path on success or `NULL`.

The public `mktemp()` emits a warning recommending `mkstemp()` or `mkdtemp()` because name-only temporary path generation is race-prone.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/mktemp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/open_memstream.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/open_memstream.c

Implements `open_memstream()` with a `funopen2()` cookie tracking the caller’s `char **bufp`, `size_t *sizep`, allocated length, and current offset. Writes grow the buffer with `realloc()`, zero-fill new gaps, copy data at the offset, and update `*sizep` to `min(len, offset)`.

Seeking supports `SEEK_SET`, `SEEK_CUR` for ftell-style queries, and bounded `SEEK_END`; invalid negative or overflowing positions set `EINVAL` or `EOVERFLOW`. The returned stream is forced byte-oriented with `fwide(fp, -1)`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/open_memstream.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/open_wmemstream.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/open_wmemstream.c

Implements `open_wmemstream()` with a `funopen2()` cookie storing a wide buffer, size pointer, length, offset, and multibyte conversion state. Writes receive multibyte bytes from stdio, count/convert them to `wchar_t` values with `mbrlen()`/`mbrtowc()`, handle embedded NULs specially, grow the wide buffer, and update the exported size.

Seeking mirrors `open_memstream()` and resets the conversion state when the offset changes. The stream is forced wide-oriented with `fwide(fp, 1)`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/open_wmemstream.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/perror.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/perror.c

Implements `perror(const char *s)`. It uses a local `strerror_r()` buffer so it does not disturb `strerror()` static-buffer semantics, then prints prefix, optional `": "`, current `errno` text, and newline to `stderr`.

Null or empty prefixes suppress the separator.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/perror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/printf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/printf.c

Implements `printf()` and `printf_l()` as variadic wrappers over `vfprintf(stdout, ...)` and `vfprintf_l(stdout, loc, ...)`. The actual formatting engine is the narrow build of `vfwprintf.c`.

It defines the weak alias `printf_l -> _printf_l`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/printf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/putc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/putc.c

Provides function versions of `putc()` and `putc_unlocked()`. Both write one byte through `__sputc(c, fp)`, with the normal variant locking the target stream.

This is a thin wrapper around stdio’s buffered byte output path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/putc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/putchar.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/putchar.c

Provides function versions of `putchar()` and `putchar_unlocked()`. Both write to `stdout` through `__sputc()`, with only `putchar()` locking `stdout`.

It is the stdout-specific adapter for the same byte output path used by `putc.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/putchar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/puts.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/puts.c

Implements `puts()` by building a two-element `__siov` vector for the string and a trailing newline, then writing it to `stdout` with `__sfvwrite()` under a stream lock.

A null pointer is treated as the literal string `"(null)"`. On success it returns `'\n'`; on write failure it returns `EOF`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/puts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/putw.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/putw.c

Implements historical `putw(int, FILE *)`. It writes the raw `int` object through a one-element `__suio`/`__siov` vector and `__sfvwrite()` under the stream lock.

The return value is the raw `__sfvwrite()` result. Like `getw()`, the representation is binary and host-endian dependent.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/putw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/putwc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/putwc.c

Provides the function version of the `putwc` macro. It directly returns `fputwc(wc, fp)`.

Wide encoding, orientation, locking, and error behavior are delegated to `fputwc()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/putwc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/putwchar.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/putwchar.c

Provides the function version of `putwchar()`. It writes one wide character to `stdout` via `fputwc(wc, stdout)`.

This is the stdout-specific wide output wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/putwchar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/refill.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/refill.c

Implements `__srefill()`, the core buffer refill path used by byte input. It initializes stdio if needed, handles EOF/error state, switches read/write streams from writing to reading with a flush, frees active ungetc buffers while restoring saved unread bytes, allocates a buffer if needed, and reads through the stream’s `_read` callback.

Before reading from line-buffered or unbuffered streams, it flushes all line-buffered output streams via `_fwalk(lflush)`. It sets `__SEOF` on zero-length reads and `__SERR` on read errors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/refill.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/remove.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/remove.c

Implements `remove(const char *file)`. It uses `lstat()` to determine the path type, then calls `rmdir()` for directories and `unlink()` otherwise.

This avoids relying on filesystems that may reject `unlink(2)` on directories.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/remove.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/rewind.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/rewind.c

Implements `rewind(FILE *)`. It locks the stream, calls `fseek(fp, 0L, SEEK_SET)`, clears error and EOF state with `__sclearerr()`, and unlocks.

The function intentionally ignores the `fseek()` return value, matching the standard `rewind()` API.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/rewind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/rget.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/rget.c

Implements `__srget(FILE *)`, the slow path for `getc()` when the byte buffer is empty. It sets byte orientation, calls `__srefill()`, then returns the first byte from the newly filled buffer.

On refill failure it returns `EOF`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/rget.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/scanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/scanf.c

Implements `scanf()` and `scanf_l()` as variadic wrappers over `__svfscanf(stdin, ...)` and `__svfscanf_l(stdin, loc, ...)`. All parsing is delegated to `vfscanf.c`.

It defines the weak alias `scanf_l -> _scanf_l`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/scanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/setbuf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/setbuf.c

Implements `setbuf(FILE *fp, char *buf)` as a `setvbuf()` wrapper. A non-null buffer selects `_IOFBF` with `BUFSIZ`; a null buffer selects `_IONBF`.

The function returns no status and ignores the `setvbuf()` result.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/setbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/setbuffer.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/setbuffer.c

Implements BSD `setbuffer()` and `setlinebuf()`. `setbuffer()` calls `setvbuf()` with `_IOFBF` when a caller buffer is supplied, otherwise `_IONBF`, using the caller’s size. `setlinebuf()` calls `setvbuf(fp, NULL, _IOLBF, 0)`.

Both are compatibility wrappers over `setvbuf()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/setbuffer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/setvbuf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/setvbuf.c

Implements `setvbuf()`, validating mode and implementation size limits, locking the stream, flushing pending output, dropping unread input and ungetc state, freeing wide I/O state, freeing any malloc-owned buffer, and clearing buffering/EOF/seek-optimization flags.

It either installs caller-provided storage, allocates a buffer, or falls back to the one-byte unbuffered buffer. If allocation cannot honor the requested buffer size, it may return `-1` while still leaving the stream in a usable fallback buffering mode.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/setvbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/snprintf_ss.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/snprintf_ss.c

Implements `snprintf_ss()` as a variadic wrapper around `vsnprintf_ss()`. It only manages the `va_list` and returns the delegated result.

The file defines the weak alias `snprintf_ss -> _snprintf_ss` where supported.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/snprintf_ss.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/sscanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/sscanf.c

Implements `sscanf()` and `sscanf_l()` as variadic wrappers over `vsscanf()` and `vsscanf_l()`. It contains no scanning engine logic.

It defines the weak alias `sscanf_l -> _sscanf_l`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/sscanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/stdio.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/stdio.c

Provides the small system-call callbacks used by ordinary file-backed `FILE` streams: `__sread()`, `__swrite()`, `__sseek()`, and `__sclose()`. They wrap `read`, `write`, `lseek`, and `close`.

`__sread()` and `__sseek()` maintain the known seek offset flags; `__swrite()` honors append mode by seeking to end before writing and clears offset knowledge afterward. `__sclose()` closes the underlying descriptor.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/stdio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/swprintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/swprintf.c

Implements `swprintf()` and `swprintf_l()` as variadic wrappers over `vswprintf()` and `vswprintf_l()`. It only handles argument-list setup and return propagation.

It defines the weak alias `swprintf_l -> _swprintf_l`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/swprintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/swscanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/swscanf.c

Implements `swscanf()` and `swscanf_l()` as variadic wrappers over `vswscanf()` and `vswscanf_l()`. The actual wide-string scanning is delegated elsewhere.

It defines the weak alias `swscanf_l -> _swscanf_l`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/swscanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/tempnam.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/tempnam.c

Implements legacy `tempnam()`. It allocates a `MAXPATHLEN` buffer and tries candidate directories in order: `TMPDIR`, caller `dir`, `P_tmpdir`, then `_PATH_TMP`, generating `pfx + XXXXXXXXXX` names with `_mktemp()`.

It emits a warning that `tempnam()` may be unsafe and recommends `mkstemp()` or `mkdtemp()`. On total failure it preserves `errno` across the final free.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/tempnam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/tmpfile.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/tmpfile.c

Implements `tmpfile()`. It constructs a template in `_PATH_TMP`, blocks all signals while calling `mkstemp()` and immediately unlinking the name, restores the signal mask, then wraps the fd with `fdopen(fd, "w+")`.

If `fdopen()` fails, it closes the fd and restores the saved `errno`. The unlink-after-create pattern yields a temporary file removed automatically when closed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/tmpfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/tmpnam.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/tmpnam.c

Implements legacy `tmpnam()`. It uses either a static `L_tmpnam` buffer or the caller buffer, formats `P_tmpdir/tmp.<counter>.XXXXXXXXXX`, increments a static counter, and passes the template to `_mktemp()`.

The function emits an unsafe-use warning recommending `mkstemp()` or `mkdtemp()`. The static counter and static buffer make this API unsuitable for robust concurrent use.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/tmpnam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/ungetc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/ungetc.c

Implements `ungetc()`, including dynamic byte pushback growth via `__submore()`. It rejects `EOF`, initializes stdio, locks the stream, sets byte orientation, switches read/write streams into read mode if needed, clears EOF, and either backs up over an identical byte in the normal buffer or creates/extends a stack-style ungetc buffer.

The reserve buffer starts in `fp->_ubuf`; when it overflows, the code allocates `BUFSIZ`, then doubles with `realloc()` while keeping pushed-back bytes at the end of the buffer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/ungetc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/ungetwc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/ungetwc.c

Implements `ungetwc()`. It rejects `WEOF`, locks the stream, sets wide orientation, obtains the per-stream wide I/O state with `WCIO_GET()`, and pushes the wide character into a fixed wide unget buffer.

It cannot reuse byte `ungetc()` because there is no reverse conversion path for arbitrary wide strings to byte sequences. Buffer exhaustion or allocation failure returns `WEOF`; successful pushback clears stream error/EOF state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/ungetwc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vasprintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vasprintf.c

Implements `vasprintf_l()`, `vasprintf()`, `asprintf_l()`, and `asprintf()`. `vasprintf_l()` creates a string-output `FILE` with `__SWR | __SSTR | __SALC`, starts with a 128-byte malloc buffer, formats through `__vfprintf_unlocked_l()`, NUL-terminates, then shrinks the allocation to `ret + 1`.

On allocation or formatting failure it frees the buffer, sets `*str = NULL`, sets `errno = ENOMEM`, and returns `-1`. Non-locale variants use `_current_locale()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vasprintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vdprintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vdprintf.c

Implements `vdprintf_l()` and `vdprintf()`. It validates that the fd fits stdio’s short `_file` storage, checks descriptor writability with `fcntl(F_GETFL)`, builds a stack `FILE` around the fd and a `BUFSIZ` buffer, then calls `vfprintf_l()` and flushes.

The fake stream uses `__swrite` and has no close callback, so the caller’s fd remains open. Invalid access mode returns `EOF` with `EINVAL`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vdprintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vfprintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vfprintf.c

Builds the narrow `vfprintf` implementation by defining `NARROW` and including `vfwprintf.c`. This shared-source pattern compiles `vfwprintf.c` into both narrow and wide printf engines through type and helper macros.

The only direct symbol line here is the weak alias `vfprintf_l -> _vfprintf_l`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vfprintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vfscanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vfscanf.c

Implements the narrow scanf engine: `__svfscanf()`, `__svfscanf_l()`, and `__svfscanf_unlocked_l()`, with weak aliases for public `vfscanf` forms. It parses flags, width, length modifiers, assignment suppression, integers, pointers, `%n`, floats, strings, characters, and scansets.

Integer scanning uses state flags for signs, zero prefixes, `0x`, and digit presence before converting with locale-aware `strtoimax_l()`/`strtoumax_l()`. Floating parsing uses `parsefloat()` to read to the last committed valid prefix, then pushes extra bytes back with `ungetc()`. `%s`, `%c`, and `%[` support both byte and wide destinations, converting multibyte input with `mbrtowc_l()` for wide targets; scanset ranges use locale collation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vfscanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vfwprintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vfwprintf.c

Contains the shared implementation for wide `vfwprintf` and, when included with `NARROW`, narrow `vfprintf`. It handles locking wrappers, unbuffered-stream optimization through `__sbprintf()`, output batching for narrow streams, direct wide output for wide streams, flags, width, precision, size modifiers, `%n`, positional arguments, integer formatting, string conversion, floating-point formatting, locale decimal/grouping, prefixes, and padding.

Key helpers include `__ultoa()`, `__ujtoa()`, `__mbsconv()`, `__wcsconv()`, `__find_arguments()`, `__grow_type_table()`, and `exponent()`. Complexity concentrates in dual narrow/wide preprocessor behavior, positional argument table construction, locale grouping and decimal output, conversion allocation failures, and return-count overflow handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vfwprintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vfwscanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vfwscanf.c

Implements the wide scanf engine: `vfwscanf()`, `vfwscanf_l()`, and `__vfwscanf_unlocked_l()`. It reads with `__fgetwc_unlock()`, pushes back with `ungetwc()`, supports length modifiers, assignment suppression, width, `%n`, integer and pointer scanning, floating-point scanning, wide scansets, and both wide and multibyte output destinations for `%c`, `%s`, and `%[`.

Its `parsefloat()` mirrors the narrow scanner with wide characters, recognizing signs, decimal/hex mantissas, exponents, `inf`, `infinity`, and `nan(...)`, then rewinding to the last valid commit. Non-long string/char conversions convert wide input back to multibyte with `wcrtomb_l()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vfwscanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vprintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vprintf.c

Implements `vprintf()` and `vprintf_l()` as direct calls to `vfprintf(stdout, ...)` and `vfprintf_l(stdout, loc, ...)`. It adds no formatting logic.

It defines the weak alias `vprintf_l -> _vprintf_l`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vprintf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vscanf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vscanf.c

Implements `vscanf()` and `vscanf_l()` as direct calls to `__svfscanf(stdin, ...)` and `__svfscanf_l(stdin, loc, ...)`. All scan parsing is delegated to `vfscanf.c`.

It defines the weak alias `vscanf_l -> _vscanf_l`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vscanf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vsnprintf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vsnprintf.c

Implements `vsnprintf_l()`, `vsnprintf()`, `snprintf()`, and `snprintf_l()`. `vsnprintf_l()` builds a string-output `FILE` over the caller buffer, leaves room for a terminating NUL when `n > 0`, uses a dummy zero-sized buffer when `n == 0`, calls `__vfprintf_unlocked_l()`, then writes the final NUL at the current pointer.

It rejects sizes greater than `INT_MAX` with `EOVERFLOW`. Non-locale variants use `_current_locale()`, and weak aliases provide underscored libc symbol names.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/stdio/vsnprintf.c -->