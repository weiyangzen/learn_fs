# sources/distributed-fs/ceph-client/tools/include/nolibc/stdio.h

## Purpose
Implements a compact stdio-like layer over file descriptors for nolibc, including simple stream wrappers, formatted output, limited scanning, and error text.

## APIs, Types, and Functions
Defines the lightweight `FILE` fd wrapper and constants `stdin`, `stdout`, `stderr`; file helpers `fdopen`, `fopen`, `fileno`, `fflush`, `fclose`, `fgetc`, `getchar`, `fputc`, `putchar`, `fread`, `fwrite`, `fputs`, `puts`, `fgets`, and `fseek`; formatting APIs `vfprintf`, `vprintf`, `fprintf`, `printf`, `vdprintf`, `dprintf`, `vsnprintf`, `snprintf`, `vsprintf`, `sprintf`, `vasprintf`, and `asprintf`; scanning `vsscanf` and `sscanf`; plus `perror`, `setvbuf`, `strerror_r`, and `strerror`.

## Control Flow, State, and Persistence
The stream model stores only an fd in allocated `FILE` wrappers; standard streams are encoded sentinel pointers. I/O helpers call `read`, `write`, `open`, `close`, and `lseek`. The printf engine walks the format string, consumes `va_list` arguments, formats integers/strings/chars/pointers into callback sinks, and tracks truncation for snprintf. `asprintf` performs a sizing pass then allocates. State persists in heap-allocated FILE wrappers and output buffers owned by callers.

## Dependencies and Integration
Depends on `stdarg.h`, `stdlib.h`, `string.h`, `unistd.h`, `fcntl.h`, `errno.h`, and syscall wrappers. It integrates with diagnostics, getopt errors, command-line tools, and any nolibc code needing libc-style fd I/O without buffering.

## Risks and Test Signals
Risks include incomplete printf/scanf format support, no real buffering despite `setvbuf`, allocation failure in `asprintf`, format-string type mismatches, and differences from libc stream semantics. Test signals are formatted-output golden tests, snprintf truncation boundaries, fd-backed read/write tests, asprintf allocation failures, sscanf conversion tests, and stderr/perror errno output checks.
