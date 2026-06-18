# subset-b-006774 Research

Grouped research report for subset-b-006774. Each section is source-tree-aligned and delimited for reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/vdso.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/vdso.h

## Purpose
Declares perf's vDSO DSO/map helpers. It centralizes the canonical `[vdso]`, `[vdso32]`, and `[vdsox32]` names, provides `is_vdso_map()`, and exposes `dso__is_vdso()`, `machine__findnew_vdso()`, and `machine__exit_vdso()` for perf machine/thread map handling.

## Important APIs, Types, And Functions
The inline path is a pure string comparison against `VDSO__MAP_NAME`; the non-inline functions are implemented elsewhere and integrate with `struct dso`, `struct machine`, and `struct thread`. No persistent state is kept in the header, but callers use it to identify process-local synthetic DSOs. Dependencies are Linux types, string, bool, and perf util DSO/machine abstractions. Risks are mostly name drift and arch-specific vDSO aliases not matching these constants. Test signals are perf record/report cases that resolve userspace samples through vDSO mappings on native, compat 32-bit, and x32 processes.

## Control Flow
The inline path is a pure string comparison against `VDSO__MAP_NAME`; the non-inline functions are implemented elsewhere and integrate with `struct dso`, `struct machine`, and `struct thread`. No persistent state is kept in the header, but callers use it to identify process-local synthetic DSOs. Dependencies are Linux types, string, bool, and perf util DSO/machine abstractions. Risks are mostly name drift and arch-specific vDSO aliases not matching these constants. Test signals are perf record/report cases that resolve userspace samples through vDSO mappings on native, compat 32-bit, and x32 processes.

## State And Persistence
The inline path is a pure string comparison against `VDSO__MAP_NAME`; the non-inline functions are implemented elsewhere and integrate with `struct dso`, `struct machine`, and `struct thread`. No persistent state is kept in the header, but callers use it to identify process-local synthetic DSOs. Dependencies are Linux types, string, bool, and perf util DSO/machine abstractions. Risks are mostly name drift and arch-specific vDSO aliases not matching these constants. Test signals are perf record/report cases that resolve userspace samples through vDSO mappings on native, compat 32-bit, and x32 processes.

## Dependencies And Integration Points
The inline path is a pure string comparison against `VDSO__MAP_NAME`; the non-inline functions are implemented elsewhere and integrate with `struct dso`, `struct machine`, and `struct thread`. No persistent state is kept in the header, but callers use it to identify process-local synthetic DSOs. Dependencies are Linux types, string, bool, and perf util DSO/machine abstractions. Risks are mostly name drift and arch-specific vDSO aliases not matching these constants. Test signals are perf record/report cases that resolve userspace samples through vDSO mappings on native, compat 32-bit, and x32 processes.

## Risks And Edge Cases
The inline path is a pure string comparison against `VDSO__MAP_NAME`; the non-inline functions are implemented elsewhere and integrate with `struct dso`, `struct machine`, and `struct thread`. No persistent state is kept in the header, but callers use it to identify process-local synthetic DSOs. Dependencies are Linux types, string, bool, and perf util DSO/machine abstractions. Risks are mostly name drift and arch-specific vDSO aliases not matching these constants. Test signals are perf record/report cases that resolve userspace samples through vDSO mappings on native, compat 32-bit, and x32 processes.

## Test Signals
The inline path is a pure string comparison against `VDSO__MAP_NAME`; the non-inline functions are implemented elsewhere and integrate with `struct dso`, `struct machine`, and `struct thread`. No persistent state is kept in the header, but callers use it to identify process-local synthetic DSOs. Dependencies are Linux types, string, bool, and perf util DSO/machine abstractions. Risks are mostly name drift and arch-specific vDSO aliases not matching these constants. Test signals are perf record/report cases that resolve userspace samples through vDSO mappings on native, compat 32-bit, and x32 processes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/zlib.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/zlib.c

## Purpose
Implements gzip support for perf compression utilities. `gzip_decompress_to_file()` opens and mmaps an input gzip stream, inflates it with zlib in 16 KiB chunks, and writes exact byte counts to an output fd through `writen()`; `gzip_is_compressed()` checks the gzip magic bytes.

## Important APIs, Types, And Functions
Control flow is open/fstat/mmap/inflateInit2, loop over `inflate()`, write each output chunk, then unwind through `inflateEnd`, `munmap`, and `close`. State is transient zlib stream state plus file descriptors; no repository or system state is persisted except bytes written to the supplied fd. Dependencies are zlib, mmap, POSIX file APIs, `internal/lib.h`, and `util/compress.h`. Risks include zero-length or changing files during mmap, partial output on decompression failure, int truncation of `st_size` into zlib `avail_in`, and output fd side effects before an error is known. Tests should cover valid gzip, truncated/corrupt gzip, non-gzip magic, write failure, empty input, and large compressed streams.

## Control Flow
Control flow is open/fstat/mmap/inflateInit2, loop over `inflate()`, write each output chunk, then unwind through `inflateEnd`, `munmap`, and `close`. State is transient zlib stream state plus file descriptors; no repository or system state is persisted except bytes written to the supplied fd. Dependencies are zlib, mmap, POSIX file APIs, `internal/lib.h`, and `util/compress.h`. Risks include zero-length or changing files during mmap, partial output on decompression failure, int truncation of `st_size` into zlib `avail_in`, and output fd side effects before an error is known. Tests should cover valid gzip, truncated/corrupt gzip, non-gzip magic, write failure, empty input, and large compressed streams.

## State And Persistence
Control flow is open/fstat/mmap/inflateInit2, loop over `inflate()`, write each output chunk, then unwind through `inflateEnd`, `munmap`, and `close`. State is transient zlib stream state plus file descriptors; no repository or system state is persisted except bytes written to the supplied fd. Dependencies are zlib, mmap, POSIX file APIs, `internal/lib.h`, and `util/compress.h`. Risks include zero-length or changing files during mmap, partial output on decompression failure, int truncation of `st_size` into zlib `avail_in`, and output fd side effects before an error is known. Tests should cover valid gzip, truncated/corrupt gzip, non-gzip magic, write failure, empty input, and large compressed streams.

## Dependencies And Integration Points
Control flow is open/fstat/mmap/inflateInit2, loop over `inflate()`, write each output chunk, then unwind through `inflateEnd`, `munmap`, and `close`. State is transient zlib stream state plus file descriptors; no repository or system state is persisted except bytes written to the supplied fd. Dependencies are zlib, mmap, POSIX file APIs, `internal/lib.h`, and `util/compress.h`. Risks include zero-length or changing files during mmap, partial output on decompression failure, int truncation of `st_size` into zlib `avail_in`, and output fd side effects before an error is known. Tests should cover valid gzip, truncated/corrupt gzip, non-gzip magic, write failure, empty input, and large compressed streams.

## Risks And Edge Cases
Control flow is open/fstat/mmap/inflateInit2, loop over `inflate()`, write each output chunk, then unwind through `inflateEnd`, `munmap`, and `close`. State is transient zlib stream state plus file descriptors; no repository or system state is persisted except bytes written to the supplied fd. Dependencies are zlib, mmap, POSIX file APIs, `internal/lib.h`, and `util/compress.h`. Risks include zero-length or changing files during mmap, partial output on decompression failure, int truncation of `st_size` into zlib `avail_in`, and output fd side effects before an error is known. Tests should cover valid gzip, truncated/corrupt gzip, non-gzip magic, write failure, empty input, and large compressed streams.

## Test Signals
Control flow is open/fstat/mmap/inflateInit2, loop over `inflate()`, write each output chunk, then unwind through `inflateEnd`, `munmap`, and `close`. State is transient zlib stream state plus file descriptors; no repository or system state is persisted except bytes written to the supplied fd. Dependencies are zlib, mmap, POSIX file APIs, `internal/lib.h`, and `util/compress.h`. Risks include zero-length or changing files during mmap, partial output on decompression failure, int truncation of `st_size` into zlib `avail_in`, and output fd side effects before an error is known. Tests should cover valid gzip, truncated/corrupt gzip, non-gzip magic, write failure, empty input, and large compressed streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/zlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/zstd.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/zstd.c

## Purpose
Provides streaming zstd compression/decompression wrappers for perf record payloads. `zstd_init()` stores the compression level, `zstd_fini()` frees streams, `zstd_compress_stream_to_records()` compresses source bytes into bounded records with caller-supplied record headers, and `zstd_decompress_stream()` expands a compressed buffer.

## Important APIs, Types, And Functions
Compression lazily creates and initializes a `ZSTD_CStream`, repeatedly reserves header space with `process_header(record, 0)`, compresses into at most `max_record_size`, flushes the stream, and then finalizes the header with the produced size. Decompression lazily creates a `ZSTD_DStream` and loops until all input is consumed. State persists only inside `struct zstd_data` between calls, especially reusable streams. Dependencies are libzstd types from `util/compress.h` and perf `pr_err()` logging. Risks include pointer arithmetic on `void *`, insufficient `dst_size` accounting around header reservations, falling back to copying uncompressed data on compression error without a clear record marker, and stream reuse across logically independent frames. Test signals are round-trip compression, max-record boundary tests, tiny destination buffers, malformed zstd input, and repeated init/fini cycles.

## Control Flow
Compression lazily creates and initializes a `ZSTD_CStream`, repeatedly reserves header space with `process_header(record, 0)`, compresses into at most `max_record_size`, flushes the stream, and then finalizes the header with the produced size. Decompression lazily creates a `ZSTD_DStream` and loops until all input is consumed. State persists only inside `struct zstd_data` between calls, especially reusable streams. Dependencies are libzstd types from `util/compress.h` and perf `pr_err()` logging. Risks include pointer arithmetic on `void *`, insufficient `dst_size` accounting around header reservations, falling back to copying uncompressed data on compression error without a clear record marker, and stream reuse across logically independent frames. Test signals are round-trip compression, max-record boundary tests, tiny destination buffers, malformed zstd input, and repeated init/fini cycles.

## State And Persistence
Compression lazily creates and initializes a `ZSTD_CStream`, repeatedly reserves header space with `process_header(record, 0)`, compresses into at most `max_record_size`, flushes the stream, and then finalizes the header with the produced size. Decompression lazily creates a `ZSTD_DStream` and loops until all input is consumed. State persists only inside `struct zstd_data` between calls, especially reusable streams. Dependencies are libzstd types from `util/compress.h` and perf `pr_err()` logging. Risks include pointer arithmetic on `void *`, insufficient `dst_size` accounting around header reservations, falling back to copying uncompressed data on compression error without a clear record marker, and stream reuse across logically independent frames. Test signals are round-trip compression, max-record boundary tests, tiny destination buffers, malformed zstd input, and repeated init/fini cycles.

## Dependencies And Integration Points
Compression lazily creates and initializes a `ZSTD_CStream`, repeatedly reserves header space with `process_header(record, 0)`, compresses into at most `max_record_size`, flushes the stream, and then finalizes the header with the produced size. Decompression lazily creates a `ZSTD_DStream` and loops until all input is consumed. State persists only inside `struct zstd_data` between calls, especially reusable streams. Dependencies are libzstd types from `util/compress.h` and perf `pr_err()` logging. Risks include pointer arithmetic on `void *`, insufficient `dst_size` accounting around header reservations, falling back to copying uncompressed data on compression error without a clear record marker, and stream reuse across logically independent frames. Test signals are round-trip compression, max-record boundary tests, tiny destination buffers, malformed zstd input, and repeated init/fini cycles.

## Risks And Edge Cases
Compression lazily creates and initializes a `ZSTD_CStream`, repeatedly reserves header space with `process_header(record, 0)`, compresses into at most `max_record_size`, flushes the stream, and then finalizes the header with the produced size. Decompression lazily creates a `ZSTD_DStream` and loops until all input is consumed. State persists only inside `struct zstd_data` between calls, especially reusable streams. Dependencies are libzstd types from `util/compress.h` and perf `pr_err()` logging. Risks include pointer arithmetic on `void *`, insufficient `dst_size` accounting around header reservations, falling back to copying uncompressed data on compression error without a clear record marker, and stream reuse across logically independent frames. Test signals are round-trip compression, max-record boundary tests, tiny destination buffers, malformed zstd input, and repeated init/fini cycles.

## Test Signals
Compression lazily creates and initializes a `ZSTD_CStream`, repeatedly reserves header space with `process_header(record, 0)`, compresses into at most `max_record_size`, flushes the stream, and then finalizes the header with the produced size. Decompression lazily creates a `ZSTD_DStream` and loops until all input is consumed. State persists only inside `struct zstd_data` between calls, especially reusable streams. Dependencies are libzstd types from `util/compress.h` and perf `pr_err()` logging. Risks include pointer arithmetic on `void *`, insufficient `dst_size` accounting around header reservations, falling back to copying uncompressed data on compression error without a clear record marker, and stream reuse across logically independent frames. Test signals are round-trip compression, max-record boundary tests, tiny destination buffers, malformed zstd input, and repeated init/fini cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/zstd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/acpi/Makefile

## Purpose
Top-level ACPI tools make entry point. It imports the common scripts include, declares `.NOTPARALLEL`, and fans out `all`, `clean`, `install`, and `uninstall` to `acpidbg`, `acpidump`, `ec`, and `pfrut` subdirectories through the kernel `descend` macro.

## Important APIs, Types, And Functions
Control flow is target delegation only: aggregate targets expand to subtool targets and call `$(call descend,tools/$@,all)` or the derived clean/install/uninstall form. There is no runtime state; build state lives in subtool output directories. Dependencies are `../../scripts/Makefile.include` and each subtool Makefile. Risks include serialized builds due to `.NOTPARALLEL`, subtool naming assumptions in `$(@:_clean=)` substitutions, and install failure if a platform lacks one subtool dependency. Test signals are `make`, `make clean`, staged `make install DESTDIR=...`, and verifying each expected binary target is invoked.

## Control Flow
Control flow is target delegation only: aggregate targets expand to subtool targets and call `$(call descend,tools/$@,all)` or the derived clean/install/uninstall form. There is no runtime state; build state lives in subtool output directories. Dependencies are `../../scripts/Makefile.include` and each subtool Makefile. Risks include serialized builds due to `.NOTPARALLEL`, subtool naming assumptions in `$(@:_clean=)` substitutions, and install failure if a platform lacks one subtool dependency. Test signals are `make`, `make clean`, staged `make install DESTDIR=...`, and verifying each expected binary target is invoked.

## State And Persistence
Control flow is target delegation only: aggregate targets expand to subtool targets and call `$(call descend,tools/$@,all)` or the derived clean/install/uninstall form. There is no runtime state; build state lives in subtool output directories. Dependencies are `../../scripts/Makefile.include` and each subtool Makefile. Risks include serialized builds due to `.NOTPARALLEL`, subtool naming assumptions in `$(@:_clean=)` substitutions, and install failure if a platform lacks one subtool dependency. Test signals are `make`, `make clean`, staged `make install DESTDIR=...`, and verifying each expected binary target is invoked.

## Dependencies And Integration Points
Control flow is target delegation only: aggregate targets expand to subtool targets and call `$(call descend,tools/$@,all)` or the derived clean/install/uninstall form. There is no runtime state; build state lives in subtool output directories. Dependencies are `../../scripts/Makefile.include` and each subtool Makefile. Risks include serialized builds due to `.NOTPARALLEL`, subtool naming assumptions in `$(@:_clean=)` substitutions, and install failure if a platform lacks one subtool dependency. Test signals are `make`, `make clean`, staged `make install DESTDIR=...`, and verifying each expected binary target is invoked.

## Risks And Edge Cases
Control flow is target delegation only: aggregate targets expand to subtool targets and call `$(call descend,tools/$@,all)` or the derived clean/install/uninstall form. There is no runtime state; build state lives in subtool output directories. Dependencies are `../../scripts/Makefile.include` and each subtool Makefile. Risks include serialized builds due to `.NOTPARALLEL`, subtool naming assumptions in `$(@:_clean=)` substitutions, and install failure if a platform lacks one subtool dependency. Test signals are `make`, `make clean`, staged `make install DESTDIR=...`, and verifying each expected binary target is invoked.

## Test Signals
Control flow is target delegation only: aggregate targets expand to subtool targets and call `$(call descend,tools/$@,all)` or the derived clean/install/uninstall form. There is no runtime state; build state lives in subtool output directories. Dependencies are `../../scripts/Makefile.include` and each subtool Makefile. Risks include serialized builds due to `.NOTPARALLEL`, subtool naming assumptions in `$(@:_clean=)` substitutions, and install failure if a platform lacks one subtool dependency. Test signals are `make`, `make clean`, staged `make install DESTDIR=...`, and verifying each expected binary target is invoked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/Makefile.rules -->
# sources/distributed-fs/ceph-client/tools/power/acpi/Makefile.rules

## Purpose
Shared build/install rules for ACPI userspace tools. It maps a `TOOL` and `TOOL_OBJS` list into an output object directory, builds the tool, stages copied ACPICA kernel headers, and provides common clean/install/uninstall targets.

## Important APIs, Types, And Functions
Control flow builds `$(OUTPUT)$(TOOL)` from `$(toolobjs)`, compiles `%.c` via the configured `vpath`, creates `$(KERNEL_INCLUDE)` by copying `include/acpi`, and installs tools under `$(sbindir)`. State is build output, copied headers, and installed binaries/manpage extras from caller variables. Dependencies are `Makefile.config`, `srctree`, compiler/linker variables, and caller-defined `EXTRA_INSTALL`. Risks include stale copied ACPICA headers, `find | xargs rm` behavior with empty lists, and shared output directories colliding between tools. Test signals are per-tool compile, clean removing objects and copied includes, and DESTDIR install/uninstall checks.

## Control Flow
Control flow builds `$(OUTPUT)$(TOOL)` from `$(toolobjs)`, compiles `%.c` via the configured `vpath`, creates `$(KERNEL_INCLUDE)` by copying `include/acpi`, and installs tools under `$(sbindir)`. State is build output, copied headers, and installed binaries/manpage extras from caller variables. Dependencies are `Makefile.config`, `srctree`, compiler/linker variables, and caller-defined `EXTRA_INSTALL`. Risks include stale copied ACPICA headers, `find | xargs rm` behavior with empty lists, and shared output directories colliding between tools. Test signals are per-tool compile, clean removing objects and copied includes, and DESTDIR install/uninstall checks.

## State And Persistence
Control flow builds `$(OUTPUT)$(TOOL)` from `$(toolobjs)`, compiles `%.c` via the configured `vpath`, creates `$(KERNEL_INCLUDE)` by copying `include/acpi`, and installs tools under `$(sbindir)`. State is build output, copied headers, and installed binaries/manpage extras from caller variables. Dependencies are `Makefile.config`, `srctree`, compiler/linker variables, and caller-defined `EXTRA_INSTALL`. Risks include stale copied ACPICA headers, `find | xargs rm` behavior with empty lists, and shared output directories colliding between tools. Test signals are per-tool compile, clean removing objects and copied includes, and DESTDIR install/uninstall checks.

## Dependencies And Integration Points
Control flow builds `$(OUTPUT)$(TOOL)` from `$(toolobjs)`, compiles `%.c` via the configured `vpath`, creates `$(KERNEL_INCLUDE)` by copying `include/acpi`, and installs tools under `$(sbindir)`. State is build output, copied headers, and installed binaries/manpage extras from caller variables. Dependencies are `Makefile.config`, `srctree`, compiler/linker variables, and caller-defined `EXTRA_INSTALL`. Risks include stale copied ACPICA headers, `find | xargs rm` behavior with empty lists, and shared output directories colliding between tools. Test signals are per-tool compile, clean removing objects and copied includes, and DESTDIR install/uninstall checks.

## Risks And Edge Cases
Control flow builds `$(OUTPUT)$(TOOL)` from `$(toolobjs)`, compiles `%.c` via the configured `vpath`, creates `$(KERNEL_INCLUDE)` by copying `include/acpi`, and installs tools under `$(sbindir)`. State is build output, copied headers, and installed binaries/manpage extras from caller variables. Dependencies are `Makefile.config`, `srctree`, compiler/linker variables, and caller-defined `EXTRA_INSTALL`. Risks include stale copied ACPICA headers, `find | xargs rm` behavior with empty lists, and shared output directories colliding between tools. Test signals are per-tool compile, clean removing objects and copied includes, and DESTDIR install/uninstall checks.

## Test Signals
Control flow builds `$(OUTPUT)$(TOOL)` from `$(toolobjs)`, compiles `%.c` via the configured `vpath`, creates `$(KERNEL_INCLUDE)` by copying `include/acpi`, and installs tools under `$(sbindir)`. State is build output, copied headers, and installed binaries/manpage extras from caller variables. Dependencies are `Makefile.config`, `srctree`, compiler/linker variables, and caller-defined `EXTRA_INSTALL`. Risks include stale copied ACPICA headers, `find | xargs rm` behavior with empty lists, and shared output directories colliding between tools. Test signals are per-tool compile, clean removing objects and copied includes, and DESTDIR install/uninstall checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/Makefile.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/common/cmfsize.c -->
# sources/distributed-fs/ceph-client/tools/power/acpi/common/cmfsize.c

## Purpose
Contains the ACPICA utility helper `cm_get_file_size()`, which returns the byte length of an already-open `ACPI_FILE` without leaving the file positioned at EOF.

## Important APIs, Types, And Functions
The function saves `ftell()`, seeks to `SEEK_END`, reads size with `ftell()`, then seeks back to the saved offset. State mutation is limited to temporary file-position changes; on success the original offset is restored. Dependencies are ACPICA common headers and stdio-compatible `ACPI_FILE`. Risks include 32-bit truncation to `u32`, failure to restore position if the EOF `ftell()` path fails, and returning `ACPI_UINT32_MAX` as an error sentinel that can collide with a real 4 GiB-1 file size. Tests should exercise regular files, seek failures, large files, and callers such as `ap_get_table_from_file()`.

## Control Flow
The function saves `ftell()`, seeks to `SEEK_END`, reads size with `ftell()`, then seeks back to the saved offset. State mutation is limited to temporary file-position changes; on success the original offset is restored. Dependencies are ACPICA common headers and stdio-compatible `ACPI_FILE`. Risks include 32-bit truncation to `u32`, failure to restore position if the EOF `ftell()` path fails, and returning `ACPI_UINT32_MAX` as an error sentinel that can collide with a real 4 GiB-1 file size. Tests should exercise regular files, seek failures, large files, and callers such as `ap_get_table_from_file()`.

## State And Persistence
The function saves `ftell()`, seeks to `SEEK_END`, reads size with `ftell()`, then seeks back to the saved offset. State mutation is limited to temporary file-position changes; on success the original offset is restored. Dependencies are ACPICA common headers and stdio-compatible `ACPI_FILE`. Risks include 32-bit truncation to `u32`, failure to restore position if the EOF `ftell()` path fails, and returning `ACPI_UINT32_MAX` as an error sentinel that can collide with a real 4 GiB-1 file size. Tests should exercise regular files, seek failures, large files, and callers such as `ap_get_table_from_file()`.

## Dependencies And Integration Points
The function saves `ftell()`, seeks to `SEEK_END`, reads size with `ftell()`, then seeks back to the saved offset. State mutation is limited to temporary file-position changes; on success the original offset is restored. Dependencies are ACPICA common headers and stdio-compatible `ACPI_FILE`. Risks include 32-bit truncation to `u32`, failure to restore position if the EOF `ftell()` path fails, and returning `ACPI_UINT32_MAX` as an error sentinel that can collide with a real 4 GiB-1 file size. Tests should exercise regular files, seek failures, large files, and callers such as `ap_get_table_from_file()`.

## Risks And Edge Cases
The function saves `ftell()`, seeks to `SEEK_END`, reads size with `ftell()`, then seeks back to the saved offset. State mutation is limited to temporary file-position changes; on success the original offset is restored. Dependencies are ACPICA common headers and stdio-compatible `ACPI_FILE`. Risks include 32-bit truncation to `u32`, failure to restore position if the EOF `ftell()` path fails, and returning `ACPI_UINT32_MAX` as an error sentinel that can collide with a real 4 GiB-1 file size. Tests should exercise regular files, seek failures, large files, and callers such as `ap_get_table_from_file()`.

## Test Signals
The function saves `ftell()`, seeks to `SEEK_END`, reads size with `ftell()`, then seeks back to the saved offset. State mutation is limited to temporary file-position changes; on success the original offset is restored. Dependencies are ACPICA common headers and stdio-compatible `ACPI_FILE`. Risks include 32-bit truncation to `u32`, failure to restore position if the EOF `ftell()` path fails, and returning `ACPI_UINT32_MAX` as an error sentinel that can collide with a real 4 GiB-1 file size. Tests should exercise regular files, seek failures, large files, and callers such as `ap_get_table_from_file()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/common/cmfsize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/common/getopt.c -->
# sources/distributed-fs/ceph-client/tools/power/acpi/common/getopt.c

## Purpose
Implements ACPICA's custom option parser with global getopt-like state. It supports normal flags, required arguments (`:`), optional arguments (`+`), optional single-character suboptions (`^`), and required single-character suboptions (`|`).

## Important APIs, Types, And Functions
`acpi_getopt()` advances through compact option groups using `current_char_ptr`, updates `acpi_gbl_optind`, `acpi_gbl_optarg`, and `acpi_gbl_sub_opt_char`, and returns either an option character, `?`, or `ACPI_OPT_END`. `acpi_getopt_argument()` retrieves a follow-on argument for two-character options. Parser state is global and persistent across calls, so callers must use it as a single parser instance. Dependencies are ACPICA globals/macros and libc string APIs. Risks include non-reentrancy, optional arguments consuming the next positional argument, and callers forgetting to reset globals for multiple parses. Tests should cover grouped flags, `--`, missing arguments, `-v^` style suboptions, and illegal option diagnostics.

## Control Flow
`acpi_getopt()` advances through compact option groups using `current_char_ptr`, updates `acpi_gbl_optind`, `acpi_gbl_optarg`, and `acpi_gbl_sub_opt_char`, and returns either an option character, `?`, or `ACPI_OPT_END`. `acpi_getopt_argument()` retrieves a follow-on argument for two-character options. Parser state is global and persistent across calls, so callers must use it as a single parser instance. Dependencies are ACPICA globals/macros and libc string APIs. Risks include non-reentrancy, optional arguments consuming the next positional argument, and callers forgetting to reset globals for multiple parses. Tests should cover grouped flags, `--`, missing arguments, `-v^` style suboptions, and illegal option diagnostics.

## State And Persistence
`acpi_getopt()` advances through compact option groups using `current_char_ptr`, updates `acpi_gbl_optind`, `acpi_gbl_optarg`, and `acpi_gbl_sub_opt_char`, and returns either an option character, `?`, or `ACPI_OPT_END`. `acpi_getopt_argument()` retrieves a follow-on argument for two-character options. Parser state is global and persistent across calls, so callers must use it as a single parser instance. Dependencies are ACPICA globals/macros and libc string APIs. Risks include non-reentrancy, optional arguments consuming the next positional argument, and callers forgetting to reset globals for multiple parses. Tests should cover grouped flags, `--`, missing arguments, `-v^` style suboptions, and illegal option diagnostics.

## Dependencies And Integration Points
`acpi_getopt()` advances through compact option groups using `current_char_ptr`, updates `acpi_gbl_optind`, `acpi_gbl_optarg`, and `acpi_gbl_sub_opt_char`, and returns either an option character, `?`, or `ACPI_OPT_END`. `acpi_getopt_argument()` retrieves a follow-on argument for two-character options. Parser state is global and persistent across calls, so callers must use it as a single parser instance. Dependencies are ACPICA globals/macros and libc string APIs. Risks include non-reentrancy, optional arguments consuming the next positional argument, and callers forgetting to reset globals for multiple parses. Tests should cover grouped flags, `--`, missing arguments, `-v^` style suboptions, and illegal option diagnostics.

## Risks And Edge Cases
`acpi_getopt()` advances through compact option groups using `current_char_ptr`, updates `acpi_gbl_optind`, `acpi_gbl_optarg`, and `acpi_gbl_sub_opt_char`, and returns either an option character, `?`, or `ACPI_OPT_END`. `acpi_getopt_argument()` retrieves a follow-on argument for two-character options. Parser state is global and persistent across calls, so callers must use it as a single parser instance. Dependencies are ACPICA globals/macros and libc string APIs. Risks include non-reentrancy, optional arguments consuming the next positional argument, and callers forgetting to reset globals for multiple parses. Tests should cover grouped flags, `--`, missing arguments, `-v^` style suboptions, and illegal option diagnostics.

## Test Signals
`acpi_getopt()` advances through compact option groups using `current_char_ptr`, updates `acpi_gbl_optind`, `acpi_gbl_optarg`, and `acpi_gbl_sub_opt_char`, and returns either an option character, `?`, or `ACPI_OPT_END`. `acpi_getopt_argument()` retrieves a follow-on argument for two-character options. Parser state is global and persistent across calls, so callers must use it as a single parser instance. Dependencies are ACPICA globals/macros and libc string APIs. Risks include non-reentrancy, optional arguments consuming the next positional argument, and callers forgetting to reset globals for multiple parses. Tests should cover grouped flags, `--`, missing arguments, `-v^` style suboptions, and illegal option diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/common/getopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/os_specific/service_layers/oslinuxtbl.c -->
# sources/distributed-fs/ceph-client/tools/power/acpi/os_specific/service_layers/oslinuxtbl.c

## Purpose
Linux ACPICA OS service layer for discovering, listing, mapping, and copying ACPI tables for `acpidump`. It supports firmware table reads via RSDP/RSDT/XSDT/FADT memory paths and customized table reads from `/sys/firmware/acpi/tables` plus dynamic tables.

## Important APIs, Types, And Functions
The exported flow is `acpi_os_get_table_by_address()`, `acpi_os_get_table_by_name()`, and `acpi_os_get_table_by_index()`, each forcing `osl_table_initialize()` first. Initialization either loads RSDP and mandatory firmware tables then scans RSDT/XSDT, or lists sysfs customized tables; optional dynamic SSDTs are appended. State persists in globals such as `gbl_rsdp`, `gbl_fadt`, `gbl_rsdt`, `gbl_xsdt`, table-list nodes, `gbl_table_count`, and address/revision flags. Dependencies are `acpidump.h`, ACPICA table validation, `/dev/mem` mapping supplied by `osunixmap.c`, sysfs ACPI table directories, and EFI systab parsing. Risks include root/lockdown restrictions on `/dev/mem`, races with dynamic table files, duplicate instance handling, memory leaks for the global table list, fixed `PATH_MAX` path construction, and visible source corruption in this snapshot around `acpi_os_get_table_by_name()` and `osl_can_use_xsdt()` that would break compilation. Test signals are acpidump all/by-name/by-address with customized dumping on/off, XSDT disabled modes, systems with multiple SSDTs, bad checksums, and non-root failure paths.

## Control Flow
The exported flow is `acpi_os_get_table_by_address()`, `acpi_os_get_table_by_name()`, and `acpi_os_get_table_by_index()`, each forcing `osl_table_initialize()` first. Initialization either loads RSDP and mandatory firmware tables then scans RSDT/XSDT, or lists sysfs customized tables; optional dynamic SSDTs are appended. State persists in globals such as `gbl_rsdp`, `gbl_fadt`, `gbl_rsdt`, `gbl_xsdt`, table-list nodes, `gbl_table_count`, and address/revision flags. Dependencies are `acpidump.h`, ACPICA table validation, `/dev/mem` mapping supplied by `osunixmap.c`, sysfs ACPI table directories, and EFI systab parsing. Risks include root/lockdown restrictions on `/dev/mem`, races with dynamic table files, duplicate instance handling, memory leaks for the global table list, fixed `PATH_MAX` path construction, and visible source corruption in this snapshot around `acpi_os_get_table_by_name()` and `osl_can_use_xsdt()` that would break compilation. Test signals are acpidump all/by-name/by-address with customized dumping on/off, XSDT disabled modes, systems with multiple SSDTs, bad checksums, and non-root failure paths.

## State And Persistence
The exported flow is `acpi_os_get_table_by_address()`, `acpi_os_get_table_by_name()`, and `acpi_os_get_table_by_index()`, each forcing `osl_table_initialize()` first. Initialization either loads RSDP and mandatory firmware tables then scans RSDT/XSDT, or lists sysfs customized tables; optional dynamic SSDTs are appended. State persists in globals such as `gbl_rsdp`, `gbl_fadt`, `gbl_rsdt`, `gbl_xsdt`, table-list nodes, `gbl_table_count`, and address/revision flags. Dependencies are `acpidump.h`, ACPICA table validation, `/dev/mem` mapping supplied by `osunixmap.c`, sysfs ACPI table directories, and EFI systab parsing. Risks include root/lockdown restrictions on `/dev/mem`, races with dynamic table files, duplicate instance handling, memory leaks for the global table list, fixed `PATH_MAX` path construction, and visible source corruption in this snapshot around `acpi_os_get_table_by_name()` and `osl_can_use_xsdt()` that would break compilation. Test signals are acpidump all/by-name/by-address with customized dumping on/off, XSDT disabled modes, systems with multiple SSDTs, bad checksums, and non-root failure paths.

## Dependencies And Integration Points
The exported flow is `acpi_os_get_table_by_address()`, `acpi_os_get_table_by_name()`, and `acpi_os_get_table_by_index()`, each forcing `osl_table_initialize()` first. Initialization either loads RSDP and mandatory firmware tables then scans RSDT/XSDT, or lists sysfs customized tables; optional dynamic SSDTs are appended. State persists in globals such as `gbl_rsdp`, `gbl_fadt`, `gbl_rsdt`, `gbl_xsdt`, table-list nodes, `gbl_table_count`, and address/revision flags. Dependencies are `acpidump.h`, ACPICA table validation, `/dev/mem` mapping supplied by `osunixmap.c`, sysfs ACPI table directories, and EFI systab parsing. Risks include root/lockdown restrictions on `/dev/mem`, races with dynamic table files, duplicate instance handling, memory leaks for the global table list, fixed `PATH_MAX` path construction, and visible source corruption in this snapshot around `acpi_os_get_table_by_name()` and `osl_can_use_xsdt()` that would break compilation. Test signals are acpidump all/by-name/by-address with customized dumping on/off, XSDT disabled modes, systems with multiple SSDTs, bad checksums, and non-root failure paths.

## Risks And Edge Cases
The exported flow is `acpi_os_get_table_by_address()`, `acpi_os_get_table_by_name()`, and `acpi_os_get_table_by_index()`, each forcing `osl_table_initialize()` first. Initialization either loads RSDP and mandatory firmware tables then scans RSDT/XSDT, or lists sysfs customized tables; optional dynamic SSDTs are appended. State persists in globals such as `gbl_rsdp`, `gbl_fadt`, `gbl_rsdt`, `gbl_xsdt`, table-list nodes, `gbl_table_count`, and address/revision flags. Dependencies are `acpidump.h`, ACPICA table validation, `/dev/mem` mapping supplied by `osunixmap.c`, sysfs ACPI table directories, and EFI systab parsing. Risks include root/lockdown restrictions on `/dev/mem`, races with dynamic table files, duplicate instance handling, memory leaks for the global table list, fixed `PATH_MAX` path construction, and visible source corruption in this snapshot around `acpi_os_get_table_by_name()` and `osl_can_use_xsdt()` that would break compilation. Test signals are acpidump all/by-name/by-address with customized dumping on/off, XSDT disabled modes, systems with multiple SSDTs, bad checksums, and non-root failure paths.

## Test Signals
The exported flow is `acpi_os_get_table_by_address()`, `acpi_os_get_table_by_name()`, and `acpi_os_get_table_by_index()`, each forcing `osl_table_initialize()` first. Initialization either loads RSDP and mandatory firmware tables then scans RSDT/XSDT, or lists sysfs customized tables; optional dynamic SSDTs are appended. State persists in globals such as `gbl_rsdp`, `gbl_fadt`, `gbl_rsdt`, `gbl_xsdt`, table-list nodes, `gbl_table_count`, and address/revision flags. Dependencies are `acpidump.h`, ACPICA table validation, `/dev/mem` mapping supplied by `osunixmap.c`, sysfs ACPI table directories, and EFI systab parsing. Risks include root/lockdown restrictions on `/dev/mem`, races with dynamic table files, duplicate instance handling, memory leaks for the global table list, fixed `PATH_MAX` path construction, and visible source corruption in this snapshot around `acpi_os_get_table_by_name()` and `osl_can_use_xsdt()` that would break compilation. Test signals are acpidump all/by-name/by-address with customized dumping on/off, XSDT disabled modes, systems with multiple SSDTs, bad checksums, and non-root failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/os_specific/service_layers/oslinuxtbl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/os_specific/service_layers/osunixdir.c -->
# sources/distributed-fs/ceph-client/tools/power/acpi/os_specific/service_layers/osunixdir.c

## Purpose
Provides ACPICA directory iteration wrappers for Unix-like hosts. `acpi_os_open_directory()` opens a directory with a wildcard and desired file type, `acpi_os_get_next_filename()` returns matching non-dot entries of the requested type, and `acpi_os_close_directory()` closes and frees the handle.

## Important APIs, Types, And Functions
Control flow stores `DIR *`, wildcard, requested type, and a 256-byte temporary filename buffer in `external_find_info`. Each read uses `readdir()`, `fnmatch()`, constructs a full path for `stat()`, filters directory versus non-directory, and returns a copied basename. State is the live directory stream and temp buffer. Dependencies are POSIX dirent/stat/fnmatch and ACPICA file-type constants. Risks include temp buffer overflow for names longer than 255 bytes, returning an internal pointer invalidated by the next call/close, and aborting iteration on one stat failure. Tests should include wildcard matching, file-only versus dir-only filtering, hidden entries, long names, and nonexistent directories.

## Control Flow
Control flow stores `DIR *`, wildcard, requested type, and a 256-byte temporary filename buffer in `external_find_info`. Each read uses `readdir()`, `fnmatch()`, constructs a full path for `stat()`, filters directory versus non-directory, and returns a copied basename. State is the live directory stream and temp buffer. Dependencies are POSIX dirent/stat/fnmatch and ACPICA file-type constants. Risks include temp buffer overflow for names longer than 255 bytes, returning an internal pointer invalidated by the next call/close, and aborting iteration on one stat failure. Tests should include wildcard matching, file-only versus dir-only filtering, hidden entries, long names, and nonexistent directories.

## State And Persistence
Control flow stores `DIR *`, wildcard, requested type, and a 256-byte temporary filename buffer in `external_find_info`. Each read uses `readdir()`, `fnmatch()`, constructs a full path for `stat()`, filters directory versus non-directory, and returns a copied basename. State is the live directory stream and temp buffer. Dependencies are POSIX dirent/stat/fnmatch and ACPICA file-type constants. Risks include temp buffer overflow for names longer than 255 bytes, returning an internal pointer invalidated by the next call/close, and aborting iteration on one stat failure. Tests should include wildcard matching, file-only versus dir-only filtering, hidden entries, long names, and nonexistent directories.

## Dependencies And Integration Points
Control flow stores `DIR *`, wildcard, requested type, and a 256-byte temporary filename buffer in `external_find_info`. Each read uses `readdir()`, `fnmatch()`, constructs a full path for `stat()`, filters directory versus non-directory, and returns a copied basename. State is the live directory stream and temp buffer. Dependencies are POSIX dirent/stat/fnmatch and ACPICA file-type constants. Risks include temp buffer overflow for names longer than 255 bytes, returning an internal pointer invalidated by the next call/close, and aborting iteration on one stat failure. Tests should include wildcard matching, file-only versus dir-only filtering, hidden entries, long names, and nonexistent directories.

## Risks And Edge Cases
Control flow stores `DIR *`, wildcard, requested type, and a 256-byte temporary filename buffer in `external_find_info`. Each read uses `readdir()`, `fnmatch()`, constructs a full path for `stat()`, filters directory versus non-directory, and returns a copied basename. State is the live directory stream and temp buffer. Dependencies are POSIX dirent/stat/fnmatch and ACPICA file-type constants. Risks include temp buffer overflow for names longer than 255 bytes, returning an internal pointer invalidated by the next call/close, and aborting iteration on one stat failure. Tests should include wildcard matching, file-only versus dir-only filtering, hidden entries, long names, and nonexistent directories.

## Test Signals
Control flow stores `DIR *`, wildcard, requested type, and a 256-byte temporary filename buffer in `external_find_info`. Each read uses `readdir()`, `fnmatch()`, constructs a full path for `stat()`, filters directory versus non-directory, and returns a copied basename. State is the live directory stream and temp buffer. Dependencies are POSIX dirent/stat/fnmatch and ACPICA file-type constants. Risks include temp buffer overflow for names longer than 255 bytes, returning an internal pointer invalidated by the next call/close, and aborting iteration on one stat failure. Tests should include wildcard matching, file-only versus dir-only filtering, hidden entries, long names, and nonexistent directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/os_specific/service_layers/osunixdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/os_specific/service_layers/osunixmap.c -->
# sources/distributed-fs/ceph-client/tools/power/acpi/os_specific/service_layers/osunixmap.c

## Purpose
Implements native Unix physical memory mapping for ACPICA tools. `acpi_os_map_memory()` opens `/dev/mem`, aligns the requested physical address to a page boundary, mmaps the covering range read-only, and returns an adjusted pointer; `acpi_os_unmap_memory()` reverses the offset adjustment.

## Important APIs, Types, And Functions
State is only the transient mapping; the `/dev/mem` fd is closed immediately after `mmap()`. Dependencies are `/dev/mem`, page size discovery, `mmap/munmap`, and ACPICA pointer/integer macros. Risks include privilege and kernel lockdown failures, page-size arithmetic overflow, callers needing to pass the same length used for mapping, and returning an interior pointer that must not be directly munmapped except through this helper. Test signals are successful acpidump table mapping as root, graceful failure without `/dev/mem`, unaligned physical addresses, and ASAN/valgrind checks around unmap lengths.

## Control Flow
State is only the transient mapping; the `/dev/mem` fd is closed immediately after `mmap()`. Dependencies are `/dev/mem`, page size discovery, `mmap/munmap`, and ACPICA pointer/integer macros. Risks include privilege and kernel lockdown failures, page-size arithmetic overflow, callers needing to pass the same length used for mapping, and returning an interior pointer that must not be directly munmapped except through this helper. Test signals are successful acpidump table mapping as root, graceful failure without `/dev/mem`, unaligned physical addresses, and ASAN/valgrind checks around unmap lengths.

## State And Persistence
State is only the transient mapping; the `/dev/mem` fd is closed immediately after `mmap()`. Dependencies are `/dev/mem`, page size discovery, `mmap/munmap`, and ACPICA pointer/integer macros. Risks include privilege and kernel lockdown failures, page-size arithmetic overflow, callers needing to pass the same length used for mapping, and returning an interior pointer that must not be directly munmapped except through this helper. Test signals are successful acpidump table mapping as root, graceful failure without `/dev/mem`, unaligned physical addresses, and ASAN/valgrind checks around unmap lengths.

## Dependencies And Integration Points
State is only the transient mapping; the `/dev/mem` fd is closed immediately after `mmap()`. Dependencies are `/dev/mem`, page size discovery, `mmap/munmap`, and ACPICA pointer/integer macros. Risks include privilege and kernel lockdown failures, page-size arithmetic overflow, callers needing to pass the same length used for mapping, and returning an interior pointer that must not be directly munmapped except through this helper. Test signals are successful acpidump table mapping as root, graceful failure without `/dev/mem`, unaligned physical addresses, and ASAN/valgrind checks around unmap lengths.

## Risks And Edge Cases
State is only the transient mapping; the `/dev/mem` fd is closed immediately after `mmap()`. Dependencies are `/dev/mem`, page size discovery, `mmap/munmap`, and ACPICA pointer/integer macros. Risks include privilege and kernel lockdown failures, page-size arithmetic overflow, callers needing to pass the same length used for mapping, and returning an interior pointer that must not be directly munmapped except through this helper. Test signals are successful acpidump table mapping as root, graceful failure without `/dev/mem`, unaligned physical addresses, and ASAN/valgrind checks around unmap lengths.

## Test Signals
State is only the transient mapping; the `/dev/mem` fd is closed immediately after `mmap()`. Dependencies are `/dev/mem`, page size discovery, `mmap/munmap`, and ACPICA pointer/integer macros. Risks include privilege and kernel lockdown failures, page-size arithmetic overflow, callers needing to pass the same length used for mapping, and returning an interior pointer that must not be directly munmapped except through this helper. Test signals are successful acpidump table mapping as root, graceful failure without `/dev/mem`, unaligned physical addresses, and ASAN/valgrind checks around unmap lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/os_specific/service_layers/osunixmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/os_specific/service_layers/osunixxf.c -->
# sources/distributed-fs/ceph-client/tools/power/acpi/os_specific/service_layers/osunixxf.c

## Purpose
General Unix ACPICA OS abstraction layer used by ACPICA command-line tools. It provides initialization, output redirection, memory allocation, optional memory mapping stubs, semaphore/spinlock wrappers, sleep/timer APIs, port/memory/PCI stubs, and optional thread execution.

## Important APIs, Types, And Functions
Control flow is broad but shallow: `acpi_os_initialize()` sets stdout and creates the global print lock; output functions honor ACPICA debug redirection flags; `acpi_os_get_line()` reads stdin; semaphore functions map to POSIX semaphores unless single-threaded; spinlocks are implemented as one-unit semaphores; timers use `gettimeofday`; hardware access functions mostly return dummy values for userspace tools. State includes terminal raw-mode attributes under `ACPI_EXEC_APP`, `acpi_gbl_output_file`, ACPICA print lock, allocated semaphores, and detached pthreads. Dependencies are ACPICA core headers, pthreads, semaphores, stdio, termios when enabled, and build-time feature macros. Risks include dummy hardware access hiding unsupported behavior, semaphore implementations ignoring `units` greater than one, non-detached/non-joined pthread resource leakage, Apple named semaphore quirks, and visible duplicated comment delimiter text in this source snapshot. Test signals are ACPICA tool startup/shutdown, redirected debug output, timeout paths in `acpi_os_wait_semaphore()`, line input behavior, and threaded callback execution.

## Control Flow
Control flow is broad but shallow: `acpi_os_initialize()` sets stdout and creates the global print lock; output functions honor ACPICA debug redirection flags; `acpi_os_get_line()` reads stdin; semaphore functions map to POSIX semaphores unless single-threaded; spinlocks are implemented as one-unit semaphores; timers use `gettimeofday`; hardware access functions mostly return dummy values for userspace tools. State includes terminal raw-mode attributes under `ACPI_EXEC_APP`, `acpi_gbl_output_file`, ACPICA print lock, allocated semaphores, and detached pthreads. Dependencies are ACPICA core headers, pthreads, semaphores, stdio, termios when enabled, and build-time feature macros. Risks include dummy hardware access hiding unsupported behavior, semaphore implementations ignoring `units` greater than one, non-detached/non-joined pthread resource leakage, Apple named semaphore quirks, and visible duplicated comment delimiter text in this source snapshot. Test signals are ACPICA tool startup/shutdown, redirected debug output, timeout paths in `acpi_os_wait_semaphore()`, line input behavior, and threaded callback execution.

## State And Persistence
Control flow is broad but shallow: `acpi_os_initialize()` sets stdout and creates the global print lock; output functions honor ACPICA debug redirection flags; `acpi_os_get_line()` reads stdin; semaphore functions map to POSIX semaphores unless single-threaded; spinlocks are implemented as one-unit semaphores; timers use `gettimeofday`; hardware access functions mostly return dummy values for userspace tools. State includes terminal raw-mode attributes under `ACPI_EXEC_APP`, `acpi_gbl_output_file`, ACPICA print lock, allocated semaphores, and detached pthreads. Dependencies are ACPICA core headers, pthreads, semaphores, stdio, termios when enabled, and build-time feature macros. Risks include dummy hardware access hiding unsupported behavior, semaphore implementations ignoring `units` greater than one, non-detached/non-joined pthread resource leakage, Apple named semaphore quirks, and visible duplicated comment delimiter text in this source snapshot. Test signals are ACPICA tool startup/shutdown, redirected debug output, timeout paths in `acpi_os_wait_semaphore()`, line input behavior, and threaded callback execution.

## Dependencies And Integration Points
Control flow is broad but shallow: `acpi_os_initialize()` sets stdout and creates the global print lock; output functions honor ACPICA debug redirection flags; `acpi_os_get_line()` reads stdin; semaphore functions map to POSIX semaphores unless single-threaded; spinlocks are implemented as one-unit semaphores; timers use `gettimeofday`; hardware access functions mostly return dummy values for userspace tools. State includes terminal raw-mode attributes under `ACPI_EXEC_APP`, `acpi_gbl_output_file`, ACPICA print lock, allocated semaphores, and detached pthreads. Dependencies are ACPICA core headers, pthreads, semaphores, stdio, termios when enabled, and build-time feature macros. Risks include dummy hardware access hiding unsupported behavior, semaphore implementations ignoring `units` greater than one, non-detached/non-joined pthread resource leakage, Apple named semaphore quirks, and visible duplicated comment delimiter text in this source snapshot. Test signals are ACPICA tool startup/shutdown, redirected debug output, timeout paths in `acpi_os_wait_semaphore()`, line input behavior, and threaded callback execution.

## Risks And Edge Cases
Control flow is broad but shallow: `acpi_os_initialize()` sets stdout and creates the global print lock; output functions honor ACPICA debug redirection flags; `acpi_os_get_line()` reads stdin; semaphore functions map to POSIX semaphores unless single-threaded; spinlocks are implemented as one-unit semaphores; timers use `gettimeofday`; hardware access functions mostly return dummy values for userspace tools. State includes terminal raw-mode attributes under `ACPI_EXEC_APP`, `acpi_gbl_output_file`, ACPICA print lock, allocated semaphores, and detached pthreads. Dependencies are ACPICA core headers, pthreads, semaphores, stdio, termios when enabled, and build-time feature macros. Risks include dummy hardware access hiding unsupported behavior, semaphore implementations ignoring `units` greater than one, non-detached/non-joined pthread resource leakage, Apple named semaphore quirks, and visible duplicated comment delimiter text in this source snapshot. Test signals are ACPICA tool startup/shutdown, redirected debug output, timeout paths in `acpi_os_wait_semaphore()`, line input behavior, and threaded callback execution.

## Test Signals
Control flow is broad but shallow: `acpi_os_initialize()` sets stdout and creates the global print lock; output functions honor ACPICA debug redirection flags; `acpi_os_get_line()` reads stdin; semaphore functions map to POSIX semaphores unless single-threaded; spinlocks are implemented as one-unit semaphores; timers use `gettimeofday`; hardware access functions mostly return dummy values for userspace tools. State includes terminal raw-mode attributes under `ACPI_EXEC_APP`, `acpi_gbl_output_file`, ACPICA print lock, allocated semaphores, and detached pthreads. Dependencies are ACPICA core headers, pthreads, semaphores, stdio, termios when enabled, and build-time feature macros. Risks include dummy hardware access hiding unsupported behavior, semaphore implementations ignoring `units` greater than one, non-detached/non-joined pthread resource leakage, Apple named semaphore quirks, and visible duplicated comment delimiter text in this source snapshot. Test signals are ACPICA tool startup/shutdown, redirected debug output, timeout paths in `acpi_os_wait_semaphore()`, line input behavior, and threaded callback execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/os_specific/service_layers/osunixxf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidbg/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidbg/Makefile

## Purpose
Builds the `acpidbg` userspace AML debugger bridge. It includes ACPI Makefile configuration, sets `TOOL=acpidbg`, searches ACPICA/common/service-layer sources through `vpath`, adds `-DACPI_APPLICATION -DACPI_SINGLE_THREAD -DACPI_DEBUGGER`, links pthread, and delegates rules to `Makefile.rules`.

## Important APIs, Types, And Functions
The build produces one object, `acpidbg.o`, but inherits common output, install, and copied-header behavior. State is object/binary output. Dependencies are ACPICA headers, the kernel `circ_buf.h`, pthread linkage, and the common rule file. Risks include macro mismatch (`ACPI_SINGLE_THREAD` versus code paths expecting `ACPI_SINGLE_THREADED` elsewhere), debugfs interface availability only at runtime, and broad `vpath` hiding source selection mistakes. Test signals are successful build, link with pthread, and `acpidbg -h` plus open-failure behavior when debugfs is absent.

## Control Flow
The build produces one object, `acpidbg.o`, but inherits common output, install, and copied-header behavior. State is object/binary output. Dependencies are ACPICA headers, the kernel `circ_buf.h`, pthread linkage, and the common rule file. Risks include macro mismatch (`ACPI_SINGLE_THREAD` versus code paths expecting `ACPI_SINGLE_THREADED` elsewhere), debugfs interface availability only at runtime, and broad `vpath` hiding source selection mistakes. Test signals are successful build, link with pthread, and `acpidbg -h` plus open-failure behavior when debugfs is absent.

## State And Persistence
The build produces one object, `acpidbg.o`, but inherits common output, install, and copied-header behavior. State is object/binary output. Dependencies are ACPICA headers, the kernel `circ_buf.h`, pthread linkage, and the common rule file. Risks include macro mismatch (`ACPI_SINGLE_THREAD` versus code paths expecting `ACPI_SINGLE_THREADED` elsewhere), debugfs interface availability only at runtime, and broad `vpath` hiding source selection mistakes. Test signals are successful build, link with pthread, and `acpidbg -h` plus open-failure behavior when debugfs is absent.

## Dependencies And Integration Points
The build produces one object, `acpidbg.o`, but inherits common output, install, and copied-header behavior. State is object/binary output. Dependencies are ACPICA headers, the kernel `circ_buf.h`, pthread linkage, and the common rule file. Risks include macro mismatch (`ACPI_SINGLE_THREAD` versus code paths expecting `ACPI_SINGLE_THREADED` elsewhere), debugfs interface availability only at runtime, and broad `vpath` hiding source selection mistakes. Test signals are successful build, link with pthread, and `acpidbg -h` plus open-failure behavior when debugfs is absent.

## Risks And Edge Cases
The build produces one object, `acpidbg.o`, but inherits common output, install, and copied-header behavior. State is object/binary output. Dependencies are ACPICA headers, the kernel `circ_buf.h`, pthread linkage, and the common rule file. Risks include macro mismatch (`ACPI_SINGLE_THREAD` versus code paths expecting `ACPI_SINGLE_THREADED` elsewhere), debugfs interface availability only at runtime, and broad `vpath` hiding source selection mistakes. Test signals are successful build, link with pthread, and `acpidbg -h` plus open-failure behavior when debugfs is absent.

## Test Signals
The build produces one object, `acpidbg.o`, but inherits common output, install, and copied-header behavior. State is object/binary output. Dependencies are ACPICA headers, the kernel `circ_buf.h`, pthread linkage, and the common rule file. Risks include macro mismatch (`ACPI_SINGLE_THREAD` versus code paths expecting `ACPI_SINGLE_THREADED` elsewhere), debugfs interface availability only at runtime, and broad `vpath` hiding source selection mistakes. Test signals are successful build, link with pthread, and `acpidbg -h` plus open-failure behavior when debugfs is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidbg/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidbg/acpidbg.c -->
# sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidbg/acpidbg.c

## Purpose
Implements a userspace bridge to the kernel ACPI AML debugger debugfs file. It multiplexes stdin/stdout and `/sys/kernel/debug/acpi/acpidbg` using circular buffers for interactive mode and can send one command in batch mode.

## Important APIs, Types, And Functions
Control flow parses `-b`, `-f`, and `-h`; opens the debugfs file nonblocking; sets stdin/stdout nonblocking; optionally flushes old debugger output; then `select()` drives reads from stdin or batch command, writes to the kernel fd, reads debugger logs, and writes logs to stdout. State is held in two 4096-byte circular buffers, mode flags, batch command pointer/state, prompt-detection state, and the exit flag. Dependencies are debugfs ACPI debugger support, `include/linux/circ_buf.h`, ACPICA prompt constants, POSIX select/fcntl/read/write. Risks include global nonblocking changes to stdout/stdin, prompt parsing coupled to exact debugger prompt characters, fixed power-of-two buffer size assumptions, partial command/log loss if pipes close, and needing root/debugfs. Tests should cover help, missing debugfs, alternate `-f`, batch command completion, interactive echo, and full-buffer behavior.

## Control Flow
Control flow parses `-b`, `-f`, and `-h`; opens the debugfs file nonblocking; sets stdin/stdout nonblocking; optionally flushes old debugger output; then `select()` drives reads from stdin or batch command, writes to the kernel fd, reads debugger logs, and writes logs to stdout. State is held in two 4096-byte circular buffers, mode flags, batch command pointer/state, prompt-detection state, and the exit flag. Dependencies are debugfs ACPI debugger support, `include/linux/circ_buf.h`, ACPICA prompt constants, POSIX select/fcntl/read/write. Risks include global nonblocking changes to stdout/stdin, prompt parsing coupled to exact debugger prompt characters, fixed power-of-two buffer size assumptions, partial command/log loss if pipes close, and needing root/debugfs. Tests should cover help, missing debugfs, alternate `-f`, batch command completion, interactive echo, and full-buffer behavior.

## State And Persistence
Control flow parses `-b`, `-f`, and `-h`; opens the debugfs file nonblocking; sets stdin/stdout nonblocking; optionally flushes old debugger output; then `select()` drives reads from stdin or batch command, writes to the kernel fd, reads debugger logs, and writes logs to stdout. State is held in two 4096-byte circular buffers, mode flags, batch command pointer/state, prompt-detection state, and the exit flag. Dependencies are debugfs ACPI debugger support, `include/linux/circ_buf.h`, ACPICA prompt constants, POSIX select/fcntl/read/write. Risks include global nonblocking changes to stdout/stdin, prompt parsing coupled to exact debugger prompt characters, fixed power-of-two buffer size assumptions, partial command/log loss if pipes close, and needing root/debugfs. Tests should cover help, missing debugfs, alternate `-f`, batch command completion, interactive echo, and full-buffer behavior.

## Dependencies And Integration Points
Control flow parses `-b`, `-f`, and `-h`; opens the debugfs file nonblocking; sets stdin/stdout nonblocking; optionally flushes old debugger output; then `select()` drives reads from stdin or batch command, writes to the kernel fd, reads debugger logs, and writes logs to stdout. State is held in two 4096-byte circular buffers, mode flags, batch command pointer/state, prompt-detection state, and the exit flag. Dependencies are debugfs ACPI debugger support, `include/linux/circ_buf.h`, ACPICA prompt constants, POSIX select/fcntl/read/write. Risks include global nonblocking changes to stdout/stdin, prompt parsing coupled to exact debugger prompt characters, fixed power-of-two buffer size assumptions, partial command/log loss if pipes close, and needing root/debugfs. Tests should cover help, missing debugfs, alternate `-f`, batch command completion, interactive echo, and full-buffer behavior.

## Risks And Edge Cases
Control flow parses `-b`, `-f`, and `-h`; opens the debugfs file nonblocking; sets stdin/stdout nonblocking; optionally flushes old debugger output; then `select()` drives reads from stdin or batch command, writes to the kernel fd, reads debugger logs, and writes logs to stdout. State is held in two 4096-byte circular buffers, mode flags, batch command pointer/state, prompt-detection state, and the exit flag. Dependencies are debugfs ACPI debugger support, `include/linux/circ_buf.h`, ACPICA prompt constants, POSIX select/fcntl/read/write. Risks include global nonblocking changes to stdout/stdin, prompt parsing coupled to exact debugger prompt characters, fixed power-of-two buffer size assumptions, partial command/log loss if pipes close, and needing root/debugfs. Tests should cover help, missing debugfs, alternate `-f`, batch command completion, interactive echo, and full-buffer behavior.

## Test Signals
Control flow parses `-b`, `-f`, and `-h`; opens the debugfs file nonblocking; sets stdin/stdout nonblocking; optionally flushes old debugger output; then `select()` drives reads from stdin or batch command, writes to the kernel fd, reads debugger logs, and writes logs to stdout. State is held in two 4096-byte circular buffers, mode flags, batch command pointer/state, prompt-detection state, and the exit flag. Dependencies are debugfs ACPI debugger support, `include/linux/circ_buf.h`, ACPICA prompt constants, POSIX select/fcntl/read/write. Risks include global nonblocking changes to stdout/stdin, prompt parsing coupled to exact debugger prompt characters, fixed power-of-two buffer size assumptions, partial command/log loss if pipes close, and needing root/debugfs. Tests should cover help, missing debugfs, alternate `-f`, batch command completion, interactive echo, and full-buffer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidbg/acpidbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/Makefile

## Purpose
Builds and installs `acpidump`. It compiles local dump modules, ACPICA common utilities, Unix service-layer files, ACPICA table/utility modules from the kernel tree, and installs the `acpidump.8` man page.

## Important APIs, Types, And Functions
Control flow is declarative: `TOOL_OBJS` lists dump logic, OS-specific table access, file helpers, getopt, and ACPICA support routines; common `Makefile.rules` handles compilation/link/install. State is build output plus optional installed binary/manpage. Dependencies are ACPICA headers/source files, common ACPI make config, `osunixmap`, `oslinuxtbl`, and manpage source. Risks include tight coupling to kernel ACPICA internal filenames, copied header drift, and requiring platform-specific service-layer objects to satisfy `acpi_os_get_table_*`. Test signals are build, `acpidump -h`, summary mode, binary mode, and staged manpage install/uninstall.

## Control Flow
Control flow is declarative: `TOOL_OBJS` lists dump logic, OS-specific table access, file helpers, getopt, and ACPICA support routines; common `Makefile.rules` handles compilation/link/install. State is build output plus optional installed binary/manpage. Dependencies are ACPICA headers/source files, common ACPI make config, `osunixmap`, `oslinuxtbl`, and manpage source. Risks include tight coupling to kernel ACPICA internal filenames, copied header drift, and requiring platform-specific service-layer objects to satisfy `acpi_os_get_table_*`. Test signals are build, `acpidump -h`, summary mode, binary mode, and staged manpage install/uninstall.

## State And Persistence
Control flow is declarative: `TOOL_OBJS` lists dump logic, OS-specific table access, file helpers, getopt, and ACPICA support routines; common `Makefile.rules` handles compilation/link/install. State is build output plus optional installed binary/manpage. Dependencies are ACPICA headers/source files, common ACPI make config, `osunixmap`, `oslinuxtbl`, and manpage source. Risks include tight coupling to kernel ACPICA internal filenames, copied header drift, and requiring platform-specific service-layer objects to satisfy `acpi_os_get_table_*`. Test signals are build, `acpidump -h`, summary mode, binary mode, and staged manpage install/uninstall.

## Dependencies And Integration Points
Control flow is declarative: `TOOL_OBJS` lists dump logic, OS-specific table access, file helpers, getopt, and ACPICA support routines; common `Makefile.rules` handles compilation/link/install. State is build output plus optional installed binary/manpage. Dependencies are ACPICA headers/source files, common ACPI make config, `osunixmap`, `oslinuxtbl`, and manpage source. Risks include tight coupling to kernel ACPICA internal filenames, copied header drift, and requiring platform-specific service-layer objects to satisfy `acpi_os_get_table_*`. Test signals are build, `acpidump -h`, summary mode, binary mode, and staged manpage install/uninstall.

## Risks And Edge Cases
Control flow is declarative: `TOOL_OBJS` lists dump logic, OS-specific table access, file helpers, getopt, and ACPICA support routines; common `Makefile.rules` handles compilation/link/install. State is build output plus optional installed binary/manpage. Dependencies are ACPICA headers/source files, common ACPI make config, `osunixmap`, `oslinuxtbl`, and manpage source. Risks include tight coupling to kernel ACPICA internal filenames, copied header drift, and requiring platform-specific service-layer objects to satisfy `acpi_os_get_table_*`. Test signals are build, `acpidump -h`, summary mode, binary mode, and staged manpage install/uninstall.

## Test Signals
Control flow is declarative: `TOOL_OBJS` lists dump logic, OS-specific table access, file helpers, getopt, and ACPICA support routines; common `Makefile.rules` handles compilation/link/install. State is build output plus optional installed binary/manpage. Dependencies are ACPICA headers/source files, common ACPI make config, `osunixmap`, `oslinuxtbl`, and manpage source. Risks include tight coupling to kernel ACPICA internal filenames, copied header drift, and requiring platform-specific service-layer objects to satisfy `acpi_os_get_table_*`. Test signals are build, `acpidump -h`, summary mode, binary mode, and staged manpage install/uninstall.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/acpidump.h -->
# sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/acpidump.h

## Purpose
Shared declarations and globals for the `acpidump` utility. It defines option-controlled globals, dump action records, action constants, maximum action/table limits, FADT offset thresholds, and prototypes for dump/file helper functions.

## Important APIs, Types, And Functions
The header uses `_DECLARE_GLOBALS` to either define or extern globals such as `gbl_summary_mode`, `gbl_binary_mode`, `gbl_dump_customized_tables`, `gbl_output_file`, and `gbl_rsdp_base`. State ownership is therefore centralized in `apmain.c` and shared with all dump modules. Dependencies are ACPICA `acpi.h`, `accommon.h`, `actables.h`, and `acapps.h`. Risks include global mutable state, `AP_MAX_ACTIONS`/`AP_MAX_ACPI_FILES` hard limits, and ABI dependence on ACPICA FADT struct layout. Test signals are compile-time one-definition behavior, mixed action parsing, and table dumps involving DSDT/FACS address fields.

## Control Flow
The header uses `_DECLARE_GLOBALS` to either define or extern globals such as `gbl_summary_mode`, `gbl_binary_mode`, `gbl_dump_customized_tables`, `gbl_output_file`, and `gbl_rsdp_base`. State ownership is therefore centralized in `apmain.c` and shared with all dump modules. Dependencies are ACPICA `acpi.h`, `accommon.h`, `actables.h`, and `acapps.h`. Risks include global mutable state, `AP_MAX_ACTIONS`/`AP_MAX_ACPI_FILES` hard limits, and ABI dependence on ACPICA FADT struct layout. Test signals are compile-time one-definition behavior, mixed action parsing, and table dumps involving DSDT/FACS address fields.

## State And Persistence
The header uses `_DECLARE_GLOBALS` to either define or extern globals such as `gbl_summary_mode`, `gbl_binary_mode`, `gbl_dump_customized_tables`, `gbl_output_file`, and `gbl_rsdp_base`. State ownership is therefore centralized in `apmain.c` and shared with all dump modules. Dependencies are ACPICA `acpi.h`, `accommon.h`, `actables.h`, and `acapps.h`. Risks include global mutable state, `AP_MAX_ACTIONS`/`AP_MAX_ACPI_FILES` hard limits, and ABI dependence on ACPICA FADT struct layout. Test signals are compile-time one-definition behavior, mixed action parsing, and table dumps involving DSDT/FACS address fields.

## Dependencies And Integration Points
The header uses `_DECLARE_GLOBALS` to either define or extern globals such as `gbl_summary_mode`, `gbl_binary_mode`, `gbl_dump_customized_tables`, `gbl_output_file`, and `gbl_rsdp_base`. State ownership is therefore centralized in `apmain.c` and shared with all dump modules. Dependencies are ACPICA `acpi.h`, `accommon.h`, `actables.h`, and `acapps.h`. Risks include global mutable state, `AP_MAX_ACTIONS`/`AP_MAX_ACPI_FILES` hard limits, and ABI dependence on ACPICA FADT struct layout. Test signals are compile-time one-definition behavior, mixed action parsing, and table dumps involving DSDT/FACS address fields.

## Risks And Edge Cases
The header uses `_DECLARE_GLOBALS` to either define or extern globals such as `gbl_summary_mode`, `gbl_binary_mode`, `gbl_dump_customized_tables`, `gbl_output_file`, and `gbl_rsdp_base`. State ownership is therefore centralized in `apmain.c` and shared with all dump modules. Dependencies are ACPICA `acpi.h`, `accommon.h`, `actables.h`, and `acapps.h`. Risks include global mutable state, `AP_MAX_ACTIONS`/`AP_MAX_ACPI_FILES` hard limits, and ABI dependence on ACPICA FADT struct layout. Test signals are compile-time one-definition behavior, mixed action parsing, and table dumps involving DSDT/FACS address fields.

## Test Signals
The header uses `_DECLARE_GLOBALS` to either define or extern globals such as `gbl_summary_mode`, `gbl_binary_mode`, `gbl_dump_customized_tables`, `gbl_output_file`, and `gbl_rsdp_base`. State ownership is therefore centralized in `apmain.c` and shared with all dump modules. Dependencies are ACPICA `acpi.h`, `accommon.h`, `actables.h`, and `acapps.h`. Risks include global mutable state, `AP_MAX_ACTIONS`/`AP_MAX_ACPI_FILES` hard limits, and ABI dependence on ACPICA FADT struct layout. Test signals are compile-time one-definition behavior, mixed action parsing, and table dumps involving DSDT/FACS address fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/acpidump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/apdump.c -->
# sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/apdump.c

## Purpose
Contains table validation and dump routines for `acpidump`. It validates headers/checksums, computes table lengths, prints summary rows, writes binary table files, or emits ASCII hex blocks compatible with `acpixtract`.

## Important APIs, Types, And Functions
Control flow routes through `ap_dump_table_buffer()`: summary mode prints only the header, binary mode calls `ap_write_to_binary_file()`, otherwise it writes a signature/address heading and hex dump. `ap_dump_all_tables()` iterates `acpi_os_get_table_by_index()` until `AE_LIMIT`; by-address and by-name paths use ACPICA OS callbacks; by-file reads from disk. State comes from global mode/output flags and returned heap table buffers that are freed after each dump. Dependencies are ACPICA checksum/table utilities, `acpidump.h`, and OS service table access. Risks include continuing after non-initial table errors, checksum warnings not being fatal, file length validation relying on header integrity, and action loops capped at 256. Tests should cover all modes, invalid signatures, bad checksums, multiple SSDTs, and corrupt binary input files.

## Control Flow
Control flow routes through `ap_dump_table_buffer()`: summary mode prints only the header, binary mode calls `ap_write_to_binary_file()`, otherwise it writes a signature/address heading and hex dump. `ap_dump_all_tables()` iterates `acpi_os_get_table_by_index()` until `AE_LIMIT`; by-address and by-name paths use ACPICA OS callbacks; by-file reads from disk. State comes from global mode/output flags and returned heap table buffers that are freed after each dump. Dependencies are ACPICA checksum/table utilities, `acpidump.h`, and OS service table access. Risks include continuing after non-initial table errors, checksum warnings not being fatal, file length validation relying on header integrity, and action loops capped at 256. Tests should cover all modes, invalid signatures, bad checksums, multiple SSDTs, and corrupt binary input files.

## State And Persistence
Control flow routes through `ap_dump_table_buffer()`: summary mode prints only the header, binary mode calls `ap_write_to_binary_file()`, otherwise it writes a signature/address heading and hex dump. `ap_dump_all_tables()` iterates `acpi_os_get_table_by_index()` until `AE_LIMIT`; by-address and by-name paths use ACPICA OS callbacks; by-file reads from disk. State comes from global mode/output flags and returned heap table buffers that are freed after each dump. Dependencies are ACPICA checksum/table utilities, `acpidump.h`, and OS service table access. Risks include continuing after non-initial table errors, checksum warnings not being fatal, file length validation relying on header integrity, and action loops capped at 256. Tests should cover all modes, invalid signatures, bad checksums, multiple SSDTs, and corrupt binary input files.

## Dependencies And Integration Points
Control flow routes through `ap_dump_table_buffer()`: summary mode prints only the header, binary mode calls `ap_write_to_binary_file()`, otherwise it writes a signature/address heading and hex dump. `ap_dump_all_tables()` iterates `acpi_os_get_table_by_index()` until `AE_LIMIT`; by-address and by-name paths use ACPICA OS callbacks; by-file reads from disk. State comes from global mode/output flags and returned heap table buffers that are freed after each dump. Dependencies are ACPICA checksum/table utilities, `acpidump.h`, and OS service table access. Risks include continuing after non-initial table errors, checksum warnings not being fatal, file length validation relying on header integrity, and action loops capped at 256. Tests should cover all modes, invalid signatures, bad checksums, multiple SSDTs, and corrupt binary input files.

## Risks And Edge Cases
Control flow routes through `ap_dump_table_buffer()`: summary mode prints only the header, binary mode calls `ap_write_to_binary_file()`, otherwise it writes a signature/address heading and hex dump. `ap_dump_all_tables()` iterates `acpi_os_get_table_by_index()` until `AE_LIMIT`; by-address and by-name paths use ACPICA OS callbacks; by-file reads from disk. State comes from global mode/output flags and returned heap table buffers that are freed after each dump. Dependencies are ACPICA checksum/table utilities, `acpidump.h`, and OS service table access. Risks include continuing after non-initial table errors, checksum warnings not being fatal, file length validation relying on header integrity, and action loops capped at 256. Tests should cover all modes, invalid signatures, bad checksums, multiple SSDTs, and corrupt binary input files.

## Test Signals
Control flow routes through `ap_dump_table_buffer()`: summary mode prints only the header, binary mode calls `ap_write_to_binary_file()`, otherwise it writes a signature/address heading and hex dump. `ap_dump_all_tables()` iterates `acpi_os_get_table_by_index()` until `AE_LIMIT`; by-address and by-name paths use ACPICA OS callbacks; by-file reads from disk. State comes from global mode/output flags and returned heap table buffers that are freed after each dump. Dependencies are ACPICA checksum/table utilities, `acpidump.h`, and OS service table access. Risks include continuing after non-initial table errors, checksum warnings not being fatal, file length validation relying on header integrity, and action loops capped at 256. Tests should cover all modes, invalid signatures, bad checksums, multiple SSDTs, and corrupt binary input files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/apdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/apfiles.c -->
# sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/apfiles.c

## Purpose
Implements `acpidump` file I/O helpers. It prompts before overwriting text output, opens redirected output files, writes individual binary table files, and reads whole binary ACPI table files into allocated memory.

## Important APIs, Types, And Functions
`ap_open_output_file()` checks existence then assigns `gbl_output_file` and filename. `ap_write_to_binary_file()` lowercases the table signature, appends an instance number and binary suffix, and writes `ap_get_table_length()` bytes. `ap_get_table_from_file()` uses `cm_get_file_size()`, allocates a zeroed buffer, and reads the complete file. State is output globals and created files. Dependencies are stdio/stat, ACPICA allocation macros, `cm_get_file_size()`, and table validation helpers. Risks include interactive overwrite prompts blocking automation, binary output filename collisions, 32-bit file size limits, and trusting table length after reading the full file. Test signals are overwrite accept/reject, binary filename generation for RSDP/SSDT instances, short reads, and redirected output close behavior.

## Control Flow
`ap_open_output_file()` checks existence then assigns `gbl_output_file` and filename. `ap_write_to_binary_file()` lowercases the table signature, appends an instance number and binary suffix, and writes `ap_get_table_length()` bytes. `ap_get_table_from_file()` uses `cm_get_file_size()`, allocates a zeroed buffer, and reads the complete file. State is output globals and created files. Dependencies are stdio/stat, ACPICA allocation macros, `cm_get_file_size()`, and table validation helpers. Risks include interactive overwrite prompts blocking automation, binary output filename collisions, 32-bit file size limits, and trusting table length after reading the full file. Test signals are overwrite accept/reject, binary filename generation for RSDP/SSDT instances, short reads, and redirected output close behavior.

## State And Persistence
`ap_open_output_file()` checks existence then assigns `gbl_output_file` and filename. `ap_write_to_binary_file()` lowercases the table signature, appends an instance number and binary suffix, and writes `ap_get_table_length()` bytes. `ap_get_table_from_file()` uses `cm_get_file_size()`, allocates a zeroed buffer, and reads the complete file. State is output globals and created files. Dependencies are stdio/stat, ACPICA allocation macros, `cm_get_file_size()`, and table validation helpers. Risks include interactive overwrite prompts blocking automation, binary output filename collisions, 32-bit file size limits, and trusting table length after reading the full file. Test signals are overwrite accept/reject, binary filename generation for RSDP/SSDT instances, short reads, and redirected output close behavior.

## Dependencies And Integration Points
`ap_open_output_file()` checks existence then assigns `gbl_output_file` and filename. `ap_write_to_binary_file()` lowercases the table signature, appends an instance number and binary suffix, and writes `ap_get_table_length()` bytes. `ap_get_table_from_file()` uses `cm_get_file_size()`, allocates a zeroed buffer, and reads the complete file. State is output globals and created files. Dependencies are stdio/stat, ACPICA allocation macros, `cm_get_file_size()`, and table validation helpers. Risks include interactive overwrite prompts blocking automation, binary output filename collisions, 32-bit file size limits, and trusting table length after reading the full file. Test signals are overwrite accept/reject, binary filename generation for RSDP/SSDT instances, short reads, and redirected output close behavior.

## Risks And Edge Cases
`ap_open_output_file()` checks existence then assigns `gbl_output_file` and filename. `ap_write_to_binary_file()` lowercases the table signature, appends an instance number and binary suffix, and writes `ap_get_table_length()` bytes. `ap_get_table_from_file()` uses `cm_get_file_size()`, allocates a zeroed buffer, and reads the complete file. State is output globals and created files. Dependencies are stdio/stat, ACPICA allocation macros, `cm_get_file_size()`, and table validation helpers. Risks include interactive overwrite prompts blocking automation, binary output filename collisions, 32-bit file size limits, and trusting table length after reading the full file. Test signals are overwrite accept/reject, binary filename generation for RSDP/SSDT instances, short reads, and redirected output close behavior.

## Test Signals
`ap_open_output_file()` checks existence then assigns `gbl_output_file` and filename. `ap_write_to_binary_file()` lowercases the table signature, appends an instance number and binary suffix, and writes `ap_get_table_length()` bytes. `ap_get_table_from_file()` uses `cm_get_file_size()`, allocates a zeroed buffer, and reads the complete file. State is output globals and created files. Dependencies are stdio/stat, ACPICA allocation macros, `cm_get_file_size()`, and table validation helpers. Risks include interactive overwrite prompts blocking automation, binary output filename collisions, 32-bit file size limits, and trusting table length after reading the full file. Test signals are overwrite accept/reject, binary filename generation for RSDP/SSDT instances, short reads, and redirected output close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/apfiles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/apmain.c -->
# sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/apmain.c

## Purpose
Main entry point and command-line driver for `acpidump`. It parses global/table options, stores requested actions, initializes ACPICA OS services, and executes dump actions in command order.

## Important APIs, Types, And Functions
`ap_do_options()` uses ACPICA getopt to set binary, summary, verbose, customized-table, XSDT, output, and RSDP-base flags, and defers `-a`, `-f`, and `-n` requests into `action_table`. If no actions exist, it inserts dump-all. `main()` initializes ACPICA, parses options, loops over actions, closes redirected output, and returns the first error. State is the global options and the fixed-size action array. Dependencies are ACPICA utility macros, `getopt.c`, `apdump.c`, `apfiles.c`, and OS table callbacks. Risks include an off-by-one check after incrementing `current_action`, global parser state, `-x -x` dual semantics, and immediate abort on the first failing action. Tests should cover help/version, mixed actions, output files, customized table toggle, RSDP override, and action overflow.

## Control Flow
`ap_do_options()` uses ACPICA getopt to set binary, summary, verbose, customized-table, XSDT, output, and RSDP-base flags, and defers `-a`, `-f`, and `-n` requests into `action_table`. If no actions exist, it inserts dump-all. `main()` initializes ACPICA, parses options, loops over actions, closes redirected output, and returns the first error. State is the global options and the fixed-size action array. Dependencies are ACPICA utility macros, `getopt.c`, `apdump.c`, `apfiles.c`, and OS table callbacks. Risks include an off-by-one check after incrementing `current_action`, global parser state, `-x -x` dual semantics, and immediate abort on the first failing action. Tests should cover help/version, mixed actions, output files, customized table toggle, RSDP override, and action overflow.

## State And Persistence
`ap_do_options()` uses ACPICA getopt to set binary, summary, verbose, customized-table, XSDT, output, and RSDP-base flags, and defers `-a`, `-f`, and `-n` requests into `action_table`. If no actions exist, it inserts dump-all. `main()` initializes ACPICA, parses options, loops over actions, closes redirected output, and returns the first error. State is the global options and the fixed-size action array. Dependencies are ACPICA utility macros, `getopt.c`, `apdump.c`, `apfiles.c`, and OS table callbacks. Risks include an off-by-one check after incrementing `current_action`, global parser state, `-x -x` dual semantics, and immediate abort on the first failing action. Tests should cover help/version, mixed actions, output files, customized table toggle, RSDP override, and action overflow.

## Dependencies And Integration Points
`ap_do_options()` uses ACPICA getopt to set binary, summary, verbose, customized-table, XSDT, output, and RSDP-base flags, and defers `-a`, `-f`, and `-n` requests into `action_table`. If no actions exist, it inserts dump-all. `main()` initializes ACPICA, parses options, loops over actions, closes redirected output, and returns the first error. State is the global options and the fixed-size action array. Dependencies are ACPICA utility macros, `getopt.c`, `apdump.c`, `apfiles.c`, and OS table callbacks. Risks include an off-by-one check after incrementing `current_action`, global parser state, `-x -x` dual semantics, and immediate abort on the first failing action. Tests should cover help/version, mixed actions, output files, customized table toggle, RSDP override, and action overflow.

## Risks And Edge Cases
`ap_do_options()` uses ACPICA getopt to set binary, summary, verbose, customized-table, XSDT, output, and RSDP-base flags, and defers `-a`, `-f`, and `-n` requests into `action_table`. If no actions exist, it inserts dump-all. `main()` initializes ACPICA, parses options, loops over actions, closes redirected output, and returns the first error. State is the global options and the fixed-size action array. Dependencies are ACPICA utility macros, `getopt.c`, `apdump.c`, `apfiles.c`, and OS table callbacks. Risks include an off-by-one check after incrementing `current_action`, global parser state, `-x -x` dual semantics, and immediate abort on the first failing action. Tests should cover help/version, mixed actions, output files, customized table toggle, RSDP override, and action overflow.

## Test Signals
`ap_do_options()` uses ACPICA getopt to set binary, summary, verbose, customized-table, XSDT, output, and RSDP-base flags, and defers `-a`, `-f`, and `-n` requests into `action_table`. If no actions exist, it inserts dump-all. `main()` initializes ACPICA, parses options, loops over actions, closes redirected output, and returns the first error. State is the global options and the fixed-size action array. Dependencies are ACPICA utility macros, `getopt.c`, `apdump.c`, `apfiles.c`, and OS table callbacks. Risks include an off-by-one check after incrementing `current_action`, global parser state, `-x -x` dual semantics, and immediate abort on the first failing action. Tests should cover help/version, mixed actions, output files, customized table toggle, RSDP override, and action overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/apmain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/ec/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/acpi/tools/ec/Makefile

## Purpose
Builds the `ec` embedded-controller debug utility. It includes common ACPI tool configuration, declares `TOOL=ec`, sets the single object `ec_access.o`, and inherits shared compile/install rules.

## Important APIs, Types, And Functions
There is no custom control flow beyond the common `Makefile.rules` target graph. Build state is the `ec_access.o` object and `ec` binary. Dependencies are the ACPI tool make configuration and standard libc headers used by `ec_access.c`. Risks are minimal, mainly that the copied comment header names the acpidump Makefile and that the resulting tool depends on debugfs at runtime. Test signals are successful build, clean, and staged install/uninstall.

## Control Flow
There is no custom control flow beyond the common `Makefile.rules` target graph. Build state is the `ec_access.o` object and `ec` binary. Dependencies are the ACPI tool make configuration and standard libc headers used by `ec_access.c`. Risks are minimal, mainly that the copied comment header names the acpidump Makefile and that the resulting tool depends on debugfs at runtime. Test signals are successful build, clean, and staged install/uninstall.

## State And Persistence
There is no custom control flow beyond the common `Makefile.rules` target graph. Build state is the `ec_access.o` object and `ec` binary. Dependencies are the ACPI tool make configuration and standard libc headers used by `ec_access.c`. Risks are minimal, mainly that the copied comment header names the acpidump Makefile and that the resulting tool depends on debugfs at runtime. Test signals are successful build, clean, and staged install/uninstall.

## Dependencies And Integration Points
There is no custom control flow beyond the common `Makefile.rules` target graph. Build state is the `ec_access.o` object and `ec` binary. Dependencies are the ACPI tool make configuration and standard libc headers used by `ec_access.c`. Risks are minimal, mainly that the copied comment header names the acpidump Makefile and that the resulting tool depends on debugfs at runtime. Test signals are successful build, clean, and staged install/uninstall.

## Risks And Edge Cases
There is no custom control flow beyond the common `Makefile.rules` target graph. Build state is the `ec_access.o` object and `ec` binary. Dependencies are the ACPI tool make configuration and standard libc headers used by `ec_access.c`. Risks are minimal, mainly that the copied comment header names the acpidump Makefile and that the resulting tool depends on debugfs at runtime. Test signals are successful build, clean, and staged install/uninstall.

## Test Signals
There is no custom control flow beyond the common `Makefile.rules` target graph. Build state is the `ec_access.o` object and `ec` binary. Dependencies are the ACPI tool make configuration and standard libc headers used by `ec_access.c`. Risks are minimal, mainly that the copied comment header names the acpidump Makefile and that the resulting tool depends on debugfs at runtime. Test signals are successful build, clean, and staged install/uninstall.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/ec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/ec/ec_access.c -->
# sources/distributed-fs/ceph-client/tools/power/acpi/tools/ec/ec_access.c

## Purpose
Command-line utility for reading and writing the ACPI embedded controller debugfs byte array at `/sys/kernel/debug/ec/ec0/io`. It can dump all 256 bytes, re-read after a sleep and mark changes, read one byte, or write one byte.

## Important APIs, Types, And Functions
`parse_opts()` enforces mutually exclusive read/write modes and hex offsets/values. `main()` opens debugfs read-only or write-only, then dispatches to `dump_ec()`, `read_ec_val()`, or `write_ec_val()`. State is global parse results and debugfs fd offset. Dependencies are root/debugfs EC support, POSIX file APIs, `err()`, getopt, and `basename()`. Risks include `uint8_t write_value = -1` making missing-value detection unreliable, rejecting value `0xff` because of `>= 255`, `atoi()` sleep parsing, and direct EC writes causing platform side effects. Test signals are help, invalid offsets, missing debugfs, dump/read output formatting, sleep diff highlighting, and write permission failure.

## Control Flow
`parse_opts()` enforces mutually exclusive read/write modes and hex offsets/values. `main()` opens debugfs read-only or write-only, then dispatches to `dump_ec()`, `read_ec_val()`, or `write_ec_val()`. State is global parse results and debugfs fd offset. Dependencies are root/debugfs EC support, POSIX file APIs, `err()`, getopt, and `basename()`. Risks include `uint8_t write_value = -1` making missing-value detection unreliable, rejecting value `0xff` because of `>= 255`, `atoi()` sleep parsing, and direct EC writes causing platform side effects. Test signals are help, invalid offsets, missing debugfs, dump/read output formatting, sleep diff highlighting, and write permission failure.

## State And Persistence
`parse_opts()` enforces mutually exclusive read/write modes and hex offsets/values. `main()` opens debugfs read-only or write-only, then dispatches to `dump_ec()`, `read_ec_val()`, or `write_ec_val()`. State is global parse results and debugfs fd offset. Dependencies are root/debugfs EC support, POSIX file APIs, `err()`, getopt, and `basename()`. Risks include `uint8_t write_value = -1` making missing-value detection unreliable, rejecting value `0xff` because of `>= 255`, `atoi()` sleep parsing, and direct EC writes causing platform side effects. Test signals are help, invalid offsets, missing debugfs, dump/read output formatting, sleep diff highlighting, and write permission failure.

## Dependencies And Integration Points
`parse_opts()` enforces mutually exclusive read/write modes and hex offsets/values. `main()` opens debugfs read-only or write-only, then dispatches to `dump_ec()`, `read_ec_val()`, or `write_ec_val()`. State is global parse results and debugfs fd offset. Dependencies are root/debugfs EC support, POSIX file APIs, `err()`, getopt, and `basename()`. Risks include `uint8_t write_value = -1` making missing-value detection unreliable, rejecting value `0xff` because of `>= 255`, `atoi()` sleep parsing, and direct EC writes causing platform side effects. Test signals are help, invalid offsets, missing debugfs, dump/read output formatting, sleep diff highlighting, and write permission failure.

## Risks And Edge Cases
`parse_opts()` enforces mutually exclusive read/write modes and hex offsets/values. `main()` opens debugfs read-only or write-only, then dispatches to `dump_ec()`, `read_ec_val()`, or `write_ec_val()`. State is global parse results and debugfs fd offset. Dependencies are root/debugfs EC support, POSIX file APIs, `err()`, getopt, and `basename()`. Risks include `uint8_t write_value = -1` making missing-value detection unreliable, rejecting value `0xff` because of `>= 255`, `atoi()` sleep parsing, and direct EC writes causing platform side effects. Test signals are help, invalid offsets, missing debugfs, dump/read output formatting, sleep diff highlighting, and write permission failure.

## Test Signals
`parse_opts()` enforces mutually exclusive read/write modes and hex offsets/values. `main()` opens debugfs read-only or write-only, then dispatches to `dump_ec()`, `read_ec_val()`, or `write_ec_val()`. State is global parse results and debugfs fd offset. Dependencies are root/debugfs EC support, POSIX file APIs, `err()`, getopt, and `basename()`. Risks include `uint8_t write_value = -1` making missing-value detection unreliable, rejecting value `0xff` because of `>= 255`, `atoi()` sleep parsing, and direct EC writes causing platform side effects. Test signals are help, invalid offsets, missing debugfs, dump/read output formatting, sleep diff highlighting, and write permission failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/ec/ec_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/pfrut/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/acpi/tools/pfrut/Makefile

## Purpose
Builds the Platform Firmware Runtime Update utility `pfrut`. It sets warning/optimization flags, injects the UAPI pfrut header path through `PFRUT_HEADER`, links libuuid, and installs/uninstalls the `pfrut.8` man page through extra targets.

## Important APIs, Types, And Functions
Control flow is inherited from `Makefile.rules`; local configuration adds `pfrut.o`, `-luuid`, and manpage install targets. State is build output and installed binary/manpage. Dependencies are the kernel UAPI `include/uapi/linux/pfrut.h`, libuuid development files, common ACPI make configuration, and target device support at runtime. Risks include build failure if uuid headers/libs are missing, header path sensitivity, and GPL-2.0+ versus shared rule assumptions. Test signals are compile/link with `-luuid`, `pfrut --help`, and staged install/uninstall of binary plus manpage.

## Control Flow
Control flow is inherited from `Makefile.rules`; local configuration adds `pfrut.o`, `-luuid`, and manpage install targets. State is build output and installed binary/manpage. Dependencies are the kernel UAPI `include/uapi/linux/pfrut.h`, libuuid development files, common ACPI make configuration, and target device support at runtime. Risks include build failure if uuid headers/libs are missing, header path sensitivity, and GPL-2.0+ versus shared rule assumptions. Test signals are compile/link with `-luuid`, `pfrut --help`, and staged install/uninstall of binary plus manpage.

## State And Persistence
Control flow is inherited from `Makefile.rules`; local configuration adds `pfrut.o`, `-luuid`, and manpage install targets. State is build output and installed binary/manpage. Dependencies are the kernel UAPI `include/uapi/linux/pfrut.h`, libuuid development files, common ACPI make configuration, and target device support at runtime. Risks include build failure if uuid headers/libs are missing, header path sensitivity, and GPL-2.0+ versus shared rule assumptions. Test signals are compile/link with `-luuid`, `pfrut --help`, and staged install/uninstall of binary plus manpage.

## Dependencies And Integration Points
Control flow is inherited from `Makefile.rules`; local configuration adds `pfrut.o`, `-luuid`, and manpage install targets. State is build output and installed binary/manpage. Dependencies are the kernel UAPI `include/uapi/linux/pfrut.h`, libuuid development files, common ACPI make configuration, and target device support at runtime. Risks include build failure if uuid headers/libs are missing, header path sensitivity, and GPL-2.0+ versus shared rule assumptions. Test signals are compile/link with `-luuid`, `pfrut --help`, and staged install/uninstall of binary plus manpage.

## Risks And Edge Cases
Control flow is inherited from `Makefile.rules`; local configuration adds `pfrut.o`, `-luuid`, and manpage install targets. State is build output and installed binary/manpage. Dependencies are the kernel UAPI `include/uapi/linux/pfrut.h`, libuuid development files, common ACPI make configuration, and target device support at runtime. Risks include build failure if uuid headers/libs are missing, header path sensitivity, and GPL-2.0+ versus shared rule assumptions. Test signals are compile/link with `-luuid`, `pfrut --help`, and staged install/uninstall of binary plus manpage.

## Test Signals
Control flow is inherited from `Makefile.rules`; local configuration adds `pfrut.o`, `-luuid`, and manpage install targets. State is build output and installed binary/manpage. Dependencies are the kernel UAPI `include/uapi/linux/pfrut.h`, libuuid development files, common ACPI make configuration, and target device support at runtime. Risks include build failure if uuid headers/libs are missing, header path sensitivity, and GPL-2.0+ versus shared rule assumptions. Test signals are compile/link with `-luuid`, `pfrut --help`, and staged install/uninstall of binary plus manpage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/pfrut/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/pfrut/pfrut.c -->
# sources/distributed-fs/ceph-client/tools/power/acpi/tools/pfrut/pfrut.c

## Purpose
User tool for ACPI Platform Firmware Runtime Update and telemetry devices. It queries update capability, loads an EFI capsule into `/dev/acpi_pfr_update0`, stages/activates updates through ioctls, configures telemetry log metadata, and reads telemetry from `/dev/acpi_pfr_telemetry0`.

## Important APIs, Types, And Functions
`parse_options()` fills global action flags and log settings. `main()` requires root, opens update and telemetry devices, handles query/getloginfo early returns, validates and sets log info, optionally sets update/log revision, mmaps and writes a capsule file, issues stage/activate/stage-activate ioctls, and optionally mmaps telemetry data into a printable buffer. State is global parsed options plus kernel device state changed by writes/ioctls. Dependencies are UAPI pfrut ioctls, libuuid for printing GUIDs, device nodes, mmap/write/ioctl, and root privileges. Risks include firmware update side effects, global option combinations not mutually exclusive, printing a `write()` ssize_t with `%d`, missing cleanup on some log mmap paths, and telemetry treated as NUL-terminated text after copying raw bytes. Test signals are help, non-root rejection, missing devices, query capability, invalid log settings, capsule open/mmap/write failures, and ioctl return propagation.

## Control Flow
`parse_options()` fills global action flags and log settings. `main()` requires root, opens update and telemetry devices, handles query/getloginfo early returns, validates and sets log info, optionally sets update/log revision, mmaps and writes a capsule file, issues stage/activate/stage-activate ioctls, and optionally mmaps telemetry data into a printable buffer. State is global parsed options plus kernel device state changed by writes/ioctls. Dependencies are UAPI pfrut ioctls, libuuid for printing GUIDs, device nodes, mmap/write/ioctl, and root privileges. Risks include firmware update side effects, global option combinations not mutually exclusive, printing a `write()` ssize_t with `%d`, missing cleanup on some log mmap paths, and telemetry treated as NUL-terminated text after copying raw bytes. Test signals are help, non-root rejection, missing devices, query capability, invalid log settings, capsule open/mmap/write failures, and ioctl return propagation.

## State And Persistence
`parse_options()` fills global action flags and log settings. `main()` requires root, opens update and telemetry devices, handles query/getloginfo early returns, validates and sets log info, optionally sets update/log revision, mmaps and writes a capsule file, issues stage/activate/stage-activate ioctls, and optionally mmaps telemetry data into a printable buffer. State is global parsed options plus kernel device state changed by writes/ioctls. Dependencies are UAPI pfrut ioctls, libuuid for printing GUIDs, device nodes, mmap/write/ioctl, and root privileges. Risks include firmware update side effects, global option combinations not mutually exclusive, printing a `write()` ssize_t with `%d`, missing cleanup on some log mmap paths, and telemetry treated as NUL-terminated text after copying raw bytes. Test signals are help, non-root rejection, missing devices, query capability, invalid log settings, capsule open/mmap/write failures, and ioctl return propagation.

## Dependencies And Integration Points
`parse_options()` fills global action flags and log settings. `main()` requires root, opens update and telemetry devices, handles query/getloginfo early returns, validates and sets log info, optionally sets update/log revision, mmaps and writes a capsule file, issues stage/activate/stage-activate ioctls, and optionally mmaps telemetry data into a printable buffer. State is global parsed options plus kernel device state changed by writes/ioctls. Dependencies are UAPI pfrut ioctls, libuuid for printing GUIDs, device nodes, mmap/write/ioctl, and root privileges. Risks include firmware update side effects, global option combinations not mutually exclusive, printing a `write()` ssize_t with `%d`, missing cleanup on some log mmap paths, and telemetry treated as NUL-terminated text after copying raw bytes. Test signals are help, non-root rejection, missing devices, query capability, invalid log settings, capsule open/mmap/write failures, and ioctl return propagation.

## Risks And Edge Cases
`parse_options()` fills global action flags and log settings. `main()` requires root, opens update and telemetry devices, handles query/getloginfo early returns, validates and sets log info, optionally sets update/log revision, mmaps and writes a capsule file, issues stage/activate/stage-activate ioctls, and optionally mmaps telemetry data into a printable buffer. State is global parsed options plus kernel device state changed by writes/ioctls. Dependencies are UAPI pfrut ioctls, libuuid for printing GUIDs, device nodes, mmap/write/ioctl, and root privileges. Risks include firmware update side effects, global option combinations not mutually exclusive, printing a `write()` ssize_t with `%d`, missing cleanup on some log mmap paths, and telemetry treated as NUL-terminated text after copying raw bytes. Test signals are help, non-root rejection, missing devices, query capability, invalid log settings, capsule open/mmap/write failures, and ioctl return propagation.

## Test Signals
`parse_options()` fills global action flags and log settings. `main()` requires root, opens update and telemetry devices, handles query/getloginfo early returns, validates and sets log info, optionally sets update/log revision, mmaps and writes a capsule file, issues stage/activate/stage-activate ioctls, and optionally mmaps telemetry data into a printable buffer. State is global parsed options plus kernel device state changed by writes/ioctls. Dependencies are UAPI pfrut ioctls, libuuid for printing GUIDs, device nodes, mmap/write/ioctl, and root privileges. Risks include firmware update side effects, global option combinations not mutually exclusive, printing a `write()` ssize_t with `%d`, missing cleanup on some log mmap paths, and telemetry treated as NUL-terminated text after copying raw bytes. Test signals are help, non-root rejection, missing devices, query capability, invalid log settings, capsule open/mmap/write failures, and ioctl return propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/pfrut/pfrut.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/Makefile

## Purpose
Main cpupower build system. It builds `libcpupower` static/shared, the `cpupower` CLI utilities, optional NLS catalogs, optional `cpufreq-bench`, systemd unit/config/script integration, manpages, and install/uninstall targets.

## Important APIs, Types, And Functions
Control flow configures `OUTPUT`/`O=`, toolchain, DEBUG/NLS/STATIC/CPUFREQ_BENCH, source/object lists, compiler feature probes, and target rules. Shared builds create soname symlinks; static builds fold library objects into CLI objects. State includes build artifacts, generated gettext catalogs, installed libraries/headers/bin/man/systemd/completion/config files. Dependencies are gcc/binutils, libpci, librt, gettext tools when NLS is enabled, `utils/version-gen.sh`, cpupower sources, and bench submake. Risks include uninstall path typo for `$(DESTDIR)${bindir}/utils/cpupower`, output directory must preexist, NLS tool absence only warns, CPULIST/header install drift as library APIs evolve, and default `DEBUG=true` producing unstripped builds. Test signals are matrix builds for DEBUG/STATIC/NLS/CPUFREQ_BENCH, `O=` builds, staged install/uninstall, soname symlink checks, and generated systemd unit path substitution.

## Control Flow
Control flow configures `OUTPUT`/`O=`, toolchain, DEBUG/NLS/STATIC/CPUFREQ_BENCH, source/object lists, compiler feature probes, and target rules. Shared builds create soname symlinks; static builds fold library objects into CLI objects. State includes build artifacts, generated gettext catalogs, installed libraries/headers/bin/man/systemd/completion/config files. Dependencies are gcc/binutils, libpci, librt, gettext tools when NLS is enabled, `utils/version-gen.sh`, cpupower sources, and bench submake. Risks include uninstall path typo for `$(DESTDIR)${bindir}/utils/cpupower`, output directory must preexist, NLS tool absence only warns, CPULIST/header install drift as library APIs evolve, and default `DEBUG=true` producing unstripped builds. Test signals are matrix builds for DEBUG/STATIC/NLS/CPUFREQ_BENCH, `O=` builds, staged install/uninstall, soname symlink checks, and generated systemd unit path substitution.

## State And Persistence
Control flow configures `OUTPUT`/`O=`, toolchain, DEBUG/NLS/STATIC/CPUFREQ_BENCH, source/object lists, compiler feature probes, and target rules. Shared builds create soname symlinks; static builds fold library objects into CLI objects. State includes build artifacts, generated gettext catalogs, installed libraries/headers/bin/man/systemd/completion/config files. Dependencies are gcc/binutils, libpci, librt, gettext tools when NLS is enabled, `utils/version-gen.sh`, cpupower sources, and bench submake. Risks include uninstall path typo for `$(DESTDIR)${bindir}/utils/cpupower`, output directory must preexist, NLS tool absence only warns, CPULIST/header install drift as library APIs evolve, and default `DEBUG=true` producing unstripped builds. Test signals are matrix builds for DEBUG/STATIC/NLS/CPUFREQ_BENCH, `O=` builds, staged install/uninstall, soname symlink checks, and generated systemd unit path substitution.

## Dependencies And Integration Points
Control flow configures `OUTPUT`/`O=`, toolchain, DEBUG/NLS/STATIC/CPUFREQ_BENCH, source/object lists, compiler feature probes, and target rules. Shared builds create soname symlinks; static builds fold library objects into CLI objects. State includes build artifacts, generated gettext catalogs, installed libraries/headers/bin/man/systemd/completion/config files. Dependencies are gcc/binutils, libpci, librt, gettext tools when NLS is enabled, `utils/version-gen.sh`, cpupower sources, and bench submake. Risks include uninstall path typo for `$(DESTDIR)${bindir}/utils/cpupower`, output directory must preexist, NLS tool absence only warns, CPULIST/header install drift as library APIs evolve, and default `DEBUG=true` producing unstripped builds. Test signals are matrix builds for DEBUG/STATIC/NLS/CPUFREQ_BENCH, `O=` builds, staged install/uninstall, soname symlink checks, and generated systemd unit path substitution.

## Risks And Edge Cases
Control flow configures `OUTPUT`/`O=`, toolchain, DEBUG/NLS/STATIC/CPUFREQ_BENCH, source/object lists, compiler feature probes, and target rules. Shared builds create soname symlinks; static builds fold library objects into CLI objects. State includes build artifacts, generated gettext catalogs, installed libraries/headers/bin/man/systemd/completion/config files. Dependencies are gcc/binutils, libpci, librt, gettext tools when NLS is enabled, `utils/version-gen.sh`, cpupower sources, and bench submake. Risks include uninstall path typo for `$(DESTDIR)${bindir}/utils/cpupower`, output directory must preexist, NLS tool absence only warns, CPULIST/header install drift as library APIs evolve, and default `DEBUG=true` producing unstripped builds. Test signals are matrix builds for DEBUG/STATIC/NLS/CPUFREQ_BENCH, `O=` builds, staged install/uninstall, soname symlink checks, and generated systemd unit path substitution.

## Test Signals
Control flow configures `OUTPUT`/`O=`, toolchain, DEBUG/NLS/STATIC/CPUFREQ_BENCH, source/object lists, compiler feature probes, and target rules. Shared builds create soname symlinks; static builds fold library objects into CLI objects. State includes build artifacts, generated gettext catalogs, installed libraries/headers/bin/man/systemd/completion/config files. Dependencies are gcc/binutils, libpci, librt, gettext tools when NLS is enabled, `utils/version-gen.sh`, cpupower sources, and bench submake. Risks include uninstall path typo for `$(DESTDIR)${bindir}/utils/cpupower`, output directory must preexist, NLS tool absence only warns, CPULIST/header install drift as library APIs evolve, and default `DEBUG=true` producing unstripped builds. Test signals are matrix builds for DEBUG/STATIC/NLS/CPUFREQ_BENCH, `O=` builds, staged install/uninstall, soname symlink checks, and generated systemd unit path substitution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bench/Makefile

## Purpose
Submake for the `cpufreq-bench` benchmark, intended to be invoked by the parent cpupower Makefile. It chooses static versus shared libcpupower linkage, compiles four benchmark objects, defines the default config path, and installs helper scripts/config docs.

## Important APIs, Types, And Functions
Control flow refuses standalone top-level use via `MAKELEVEL`, honors `O=`, builds `cpufreq-bench`, and installs the binary under `sbindir`, plot script under `bindir`, README/script under docs, and example config under `confdir`. State is object/binary output and installed benchmark assets. Dependencies are parent-exported compiler variables, libcpupower, libm, and cpupower headers. Risks include relative `-L../` assumptions under out-of-tree builds, installing executable permission on the script/config choices, and `mkdir -p $(DESTDIR)/$(sbindir)` producing double slash harmlessly but awkwardly. Test signals are parent `make compile-bench`, static/shared modes, `O=` output, clean, and staged install.

## Control Flow
Control flow refuses standalone top-level use via `MAKELEVEL`, honors `O=`, builds `cpufreq-bench`, and installs the binary under `sbindir`, plot script under `bindir`, README/script under docs, and example config under `confdir`. State is object/binary output and installed benchmark assets. Dependencies are parent-exported compiler variables, libcpupower, libm, and cpupower headers. Risks include relative `-L../` assumptions under out-of-tree builds, installing executable permission on the script/config choices, and `mkdir -p $(DESTDIR)/$(sbindir)` producing double slash harmlessly but awkwardly. Test signals are parent `make compile-bench`, static/shared modes, `O=` output, clean, and staged install.

## State And Persistence
Control flow refuses standalone top-level use via `MAKELEVEL`, honors `O=`, builds `cpufreq-bench`, and installs the binary under `sbindir`, plot script under `bindir`, README/script under docs, and example config under `confdir`. State is object/binary output and installed benchmark assets. Dependencies are parent-exported compiler variables, libcpupower, libm, and cpupower headers. Risks include relative `-L../` assumptions under out-of-tree builds, installing executable permission on the script/config choices, and `mkdir -p $(DESTDIR)/$(sbindir)` producing double slash harmlessly but awkwardly. Test signals are parent `make compile-bench`, static/shared modes, `O=` output, clean, and staged install.

## Dependencies And Integration Points
Control flow refuses standalone top-level use via `MAKELEVEL`, honors `O=`, builds `cpufreq-bench`, and installs the binary under `sbindir`, plot script under `bindir`, README/script under docs, and example config under `confdir`. State is object/binary output and installed benchmark assets. Dependencies are parent-exported compiler variables, libcpupower, libm, and cpupower headers. Risks include relative `-L../` assumptions under out-of-tree builds, installing executable permission on the script/config choices, and `mkdir -p $(DESTDIR)/$(sbindir)` producing double slash harmlessly but awkwardly. Test signals are parent `make compile-bench`, static/shared modes, `O=` output, clean, and staged install.

## Risks And Edge Cases
Control flow refuses standalone top-level use via `MAKELEVEL`, honors `O=`, builds `cpufreq-bench`, and installs the binary under `sbindir`, plot script under `bindir`, README/script under docs, and example config under `confdir`. State is object/binary output and installed benchmark assets. Dependencies are parent-exported compiler variables, libcpupower, libm, and cpupower headers. Risks include relative `-L../` assumptions under out-of-tree builds, installing executable permission on the script/config choices, and `mkdir -p $(DESTDIR)/$(sbindir)` producing double slash harmlessly but awkwardly. Test signals are parent `make compile-bench`, static/shared modes, `O=` output, clean, and staged install.

## Test Signals
Control flow refuses standalone top-level use via `MAKELEVEL`, honors `O=`, builds `cpufreq-bench`, and installs the binary under `sbindir`, plot script under `bindir`, README/script under docs, and example config under `confdir`. State is object/binary output and installed benchmark assets. Dependencies are parent-exported compiler variables, libcpupower, libm, and cpupower headers. Risks include relative `-L../` assumptions under out-of-tree builds, installing executable permission on the script/config choices, and `mkdir -p $(DESTDIR)/$(sbindir)` producing double slash harmlessly but awkwardly. Test signals are parent `make compile-bench`, static/shared modes, `O=` output, clean, and staged install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/benchmark.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bench/benchmark.c

## Purpose
Core cpufreq benchmark loop. It calibrates a floating-point/math busy loop to approximate a target load duration, then compares average load time under the `performance` governor and a configured governor across increasing sleep/load rounds.

## Important APIs, Types, And Functions
`calculate_timespace()` times `ROUNDS()` and refines the loop count four times. `start_benchmark()` computes progress, switches governors, calibrates load, runs configured cycles with `usleep()` plus busy work, logs round/load/sleep/performance/powersave/percentage columns, and increments sleep/load times by configured steps. State changes include CPU governor writes via libcpupower and benchmark output file writes. Dependencies are `system.c`, `config.h`, `benchmark.h`, libm-heavy `ROUNDS()`, and cpufreq sysfs. Risks include divide-by-zero if calibration time or powersave time is zero, not restoring the original governor, requiring permission to change governors, timing noise from scheduling/thermal effects, and workload optimized differently by compilers. Test signals are dry runs with small cycles/rounds, governor switch failures, output column validation, and timing sanity under verbose mode.

## Control Flow
`calculate_timespace()` times `ROUNDS()` and refines the loop count four times. `start_benchmark()` computes progress, switches governors, calibrates load, runs configured cycles with `usleep()` plus busy work, logs round/load/sleep/performance/powersave/percentage columns, and increments sleep/load times by configured steps. State changes include CPU governor writes via libcpupower and benchmark output file writes. Dependencies are `system.c`, `config.h`, `benchmark.h`, libm-heavy `ROUNDS()`, and cpufreq sysfs. Risks include divide-by-zero if calibration time or powersave time is zero, not restoring the original governor, requiring permission to change governors, timing noise from scheduling/thermal effects, and workload optimized differently by compilers. Test signals are dry runs with small cycles/rounds, governor switch failures, output column validation, and timing sanity under verbose mode.

## State And Persistence
`calculate_timespace()` times `ROUNDS()` and refines the loop count four times. `start_benchmark()` computes progress, switches governors, calibrates load, runs configured cycles with `usleep()` plus busy work, logs round/load/sleep/performance/powersave/percentage columns, and increments sleep/load times by configured steps. State changes include CPU governor writes via libcpupower and benchmark output file writes. Dependencies are `system.c`, `config.h`, `benchmark.h`, libm-heavy `ROUNDS()`, and cpufreq sysfs. Risks include divide-by-zero if calibration time or powersave time is zero, not restoring the original governor, requiring permission to change governors, timing noise from scheduling/thermal effects, and workload optimized differently by compilers. Test signals are dry runs with small cycles/rounds, governor switch failures, output column validation, and timing sanity under verbose mode.

## Dependencies And Integration Points
`calculate_timespace()` times `ROUNDS()` and refines the loop count four times. `start_benchmark()` computes progress, switches governors, calibrates load, runs configured cycles with `usleep()` plus busy work, logs round/load/sleep/performance/powersave/percentage columns, and increments sleep/load times by configured steps. State changes include CPU governor writes via libcpupower and benchmark output file writes. Dependencies are `system.c`, `config.h`, `benchmark.h`, libm-heavy `ROUNDS()`, and cpufreq sysfs. Risks include divide-by-zero if calibration time or powersave time is zero, not restoring the original governor, requiring permission to change governors, timing noise from scheduling/thermal effects, and workload optimized differently by compilers. Test signals are dry runs with small cycles/rounds, governor switch failures, output column validation, and timing sanity under verbose mode.

## Risks And Edge Cases
`calculate_timespace()` times `ROUNDS()` and refines the loop count four times. `start_benchmark()` computes progress, switches governors, calibrates load, runs configured cycles with `usleep()` plus busy work, logs round/load/sleep/performance/powersave/percentage columns, and increments sleep/load times by configured steps. State changes include CPU governor writes via libcpupower and benchmark output file writes. Dependencies are `system.c`, `config.h`, `benchmark.h`, libm-heavy `ROUNDS()`, and cpufreq sysfs. Risks include divide-by-zero if calibration time or powersave time is zero, not restoring the original governor, requiring permission to change governors, timing noise from scheduling/thermal effects, and workload optimized differently by compilers. Test signals are dry runs with small cycles/rounds, governor switch failures, output column validation, and timing sanity under verbose mode.

## Test Signals
`calculate_timespace()` times `ROUNDS()` and refines the loop count four times. `start_benchmark()` computes progress, switches governors, calibrates load, runs configured cycles with `usleep()` plus busy work, logs round/load/sleep/performance/powersave/percentage columns, and increments sleep/load times by configured steps. State changes include CPU governor writes via libcpupower and benchmark output file writes. Dependencies are `system.c`, `config.h`, `benchmark.h`, libm-heavy `ROUNDS()`, and cpufreq sysfs. Risks include divide-by-zero if calibration time or powersave time is zero, not restoring the original governor, requiring permission to change governors, timing noise from scheduling/thermal effects, and workload optimized differently by compilers. Test signals are dry runs with small cycles/rounds, governor switch failures, output column validation, and timing sanity under verbose mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/benchmark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/benchmark.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bench/benchmark.h

## Purpose
Declares the benchmark entry point and defines the synthetic load macro `ROUNDS(x)`. The macro performs `x * 1000` iterations of `pow`, `sqrt`, integer xor, and `atan2` expressions to burn CPU time.

## Important APIs, Types, And Functions
Control flow is macro expansion inside calibration and benchmark loops; there is no persistent state. Dependencies are `math.h` availability in includers and `struct config` from `parse.h` or equivalent prior declarations. Risks include multiple evaluation of `x`, integer overflow in `x * 1000`, dependency on optimizer behavior, and expensive libm calls skewing benchmark portability. Test signals are successful link with `-lm`, calibration stability, and compiler warning checks under different optimization levels.

## Control Flow
Control flow is macro expansion inside calibration and benchmark loops; there is no persistent state. Dependencies are `math.h` availability in includers and `struct config` from `parse.h` or equivalent prior declarations. Risks include multiple evaluation of `x`, integer overflow in `x * 1000`, dependency on optimizer behavior, and expensive libm calls skewing benchmark portability. Test signals are successful link with `-lm`, calibration stability, and compiler warning checks under different optimization levels.

## State And Persistence
Control flow is macro expansion inside calibration and benchmark loops; there is no persistent state. Dependencies are `math.h` availability in includers and `struct config` from `parse.h` or equivalent prior declarations. Risks include multiple evaluation of `x`, integer overflow in `x * 1000`, dependency on optimizer behavior, and expensive libm calls skewing benchmark portability. Test signals are successful link with `-lm`, calibration stability, and compiler warning checks under different optimization levels.

## Dependencies And Integration Points
Control flow is macro expansion inside calibration and benchmark loops; there is no persistent state. Dependencies are `math.h` availability in includers and `struct config` from `parse.h` or equivalent prior declarations. Risks include multiple evaluation of `x`, integer overflow in `x * 1000`, dependency on optimizer behavior, and expensive libm calls skewing benchmark portability. Test signals are successful link with `-lm`, calibration stability, and compiler warning checks under different optimization levels.

## Risks And Edge Cases
Control flow is macro expansion inside calibration and benchmark loops; there is no persistent state. Dependencies are `math.h` availability in includers and `struct config` from `parse.h` or equivalent prior declarations. Risks include multiple evaluation of `x`, integer overflow in `x * 1000`, dependency on optimizer behavior, and expensive libm calls skewing benchmark portability. Test signals are successful link with `-lm`, calibration stability, and compiler warning checks under different optimization levels.

## Test Signals
Control flow is macro expansion inside calibration and benchmark loops; there is no persistent state. Dependencies are `math.h` availability in includers and `struct config` from `parse.h` or equivalent prior declarations. Risks include multiple evaluation of `x`, integer overflow in `x * 1000`, dependency on optimizer behavior, and expensive libm calls skewing benchmark portability. Test signals are successful link with `-lm`, calibration stability, and compiler warning checks under different optimization levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/benchmark.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/config.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bench/config.h

## Purpose
Holds compile-time constants for cpufreq-bench. It defines the initial calibration loop count, scheduler policy, priority aliases, and `dprintf` as either `printf` under DEBUG or a no-op otherwise.

## Important APIs, Types, And Functions
There is no control flow except preprocessor selection. State is compile-time only. Dependencies are `sched_get_priority_max/min()` and `SCHED_OTHER` being visible before priority macros are used. Risks include macro name collision with POSIX `dprintf`, priority macros evaluating scheduler functions at use sites, and DEBUG altering runtime verbosity/performance. Test signals are builds with and without DEBUG and code paths using `PRIORITY_HIGH/LOW` after including scheduler headers.

## Control Flow
There is no control flow except preprocessor selection. State is compile-time only. Dependencies are `sched_get_priority_max/min()` and `SCHED_OTHER` being visible before priority macros are used. Risks include macro name collision with POSIX `dprintf`, priority macros evaluating scheduler functions at use sites, and DEBUG altering runtime verbosity/performance. Test signals are builds with and without DEBUG and code paths using `PRIORITY_HIGH/LOW` after including scheduler headers.

## State And Persistence
There is no control flow except preprocessor selection. State is compile-time only. Dependencies are `sched_get_priority_max/min()` and `SCHED_OTHER` being visible before priority macros are used. Risks include macro name collision with POSIX `dprintf`, priority macros evaluating scheduler functions at use sites, and DEBUG altering runtime verbosity/performance. Test signals are builds with and without DEBUG and code paths using `PRIORITY_HIGH/LOW` after including scheduler headers.

## Dependencies And Integration Points
There is no control flow except preprocessor selection. State is compile-time only. Dependencies are `sched_get_priority_max/min()` and `SCHED_OTHER` being visible before priority macros are used. Risks include macro name collision with POSIX `dprintf`, priority macros evaluating scheduler functions at use sites, and DEBUG altering runtime verbosity/performance. Test signals are builds with and without DEBUG and code paths using `PRIORITY_HIGH/LOW` after including scheduler headers.

## Risks And Edge Cases
There is no control flow except preprocessor selection. State is compile-time only. Dependencies are `sched_get_priority_max/min()` and `SCHED_OTHER` being visible before priority macros are used. Risks include macro name collision with POSIX `dprintf`, priority macros evaluating scheduler functions at use sites, and DEBUG altering runtime verbosity/performance. Test signals are builds with and without DEBUG and code paths using `PRIORITY_HIGH/LOW` after including scheduler headers.

## Test Signals
There is no control flow except preprocessor selection. State is compile-time only. Dependencies are `sched_get_priority_max/min()` and `SCHED_OTHER` being visible before priority macros are used. Risks include macro name collision with POSIX `dprintf`, priority macros evaluating scheduler functions at use sites, and DEBUG altering runtime verbosity/performance. Test signals are builds with and without DEBUG and code paths using `PRIORITY_HIGH/LOW` after including scheduler headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/cpufreq-bench_plot.sh -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bench/cpufreq-bench_plot.sh

## Purpose
Helper script that converts one or more cpufreq-bench result logs into a gnuplot image. It parses `-o`, `-t`, and `-p`, validates input files, extracts load time and percentage columns, generates a temporary gnuplot script, invokes gnuplot, and removes the temp directory.

## Important APIs, Types, And Functions
State is a `mktemp -d` workspace, generated `plot_script.gpl`, temporary data files, and the final image. Dependencies are bash arrays, grep, awk, gnuplot, and the expected benchmark log schema. Risks include unquoted file paths in several commands, output extension handling where `-o name` appends current picture type before a later `-p` change, no trap cleanup on failure, and assuming load equals sleep for meaningful plots. Test signals are no-arg usage, missing file handling, single and multi-plot logs, paths with spaces, and gnuplot availability.

## Control Flow
State is a `mktemp -d` workspace, generated `plot_script.gpl`, temporary data files, and the final image. Dependencies are bash arrays, grep, awk, gnuplot, and the expected benchmark log schema. Risks include unquoted file paths in several commands, output extension handling where `-o name` appends current picture type before a later `-p` change, no trap cleanup on failure, and assuming load equals sleep for meaningful plots. Test signals are no-arg usage, missing file handling, single and multi-plot logs, paths with spaces, and gnuplot availability.

## State And Persistence
State is a `mktemp -d` workspace, generated `plot_script.gpl`, temporary data files, and the final image. Dependencies are bash arrays, grep, awk, gnuplot, and the expected benchmark log schema. Risks include unquoted file paths in several commands, output extension handling where `-o name` appends current picture type before a later `-p` change, no trap cleanup on failure, and assuming load equals sleep for meaningful plots. Test signals are no-arg usage, missing file handling, single and multi-plot logs, paths with spaces, and gnuplot availability.

## Dependencies And Integration Points
State is a `mktemp -d` workspace, generated `plot_script.gpl`, temporary data files, and the final image. Dependencies are bash arrays, grep, awk, gnuplot, and the expected benchmark log schema. Risks include unquoted file paths in several commands, output extension handling where `-o name` appends current picture type before a later `-p` change, no trap cleanup on failure, and assuming load equals sleep for meaningful plots. Test signals are no-arg usage, missing file handling, single and multi-plot logs, paths with spaces, and gnuplot availability.

## Risks And Edge Cases
State is a `mktemp -d` workspace, generated `plot_script.gpl`, temporary data files, and the final image. Dependencies are bash arrays, grep, awk, gnuplot, and the expected benchmark log schema. Risks include unquoted file paths in several commands, output extension handling where `-o name` appends current picture type before a later `-p` change, no trap cleanup on failure, and assuming load equals sleep for meaningful plots. Test signals are no-arg usage, missing file handling, single and multi-plot logs, paths with spaces, and gnuplot availability.

## Test Signals
State is a `mktemp -d` workspace, generated `plot_script.gpl`, temporary data files, and the final image. Dependencies are bash arrays, grep, awk, gnuplot, and the expected benchmark log schema. Risks include unquoted file paths in several commands, output extension handling where `-o name` appends current picture type before a later `-p` change, no trap cleanup on failure, and assuming load equals sleep for meaningful plots. Test signals are no-arg usage, missing file handling, single and multi-plot logs, paths with spaces, and gnuplot availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/cpufreq-bench_plot.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/cpufreq-bench_script.sh -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bench/cpufreq-bench_script.sh

## Purpose
Automation script for sweeping ondemand governor `up_threshold` and `sampling_rate` values with cpufreq-bench, then creating comparison plots. It writes governor tunables in sysfs, verifies actual values, stores logs under `/var/log/cpufreq-bench`, and composes plotting commands.

## Important APIs, Types, And Functions
Control flow is two nested loops in `measure()` followed by several nested plotting loops in `create_plots()`. State changes are direct sysfs writes to CPU0 ondemand tunables, benchmark log directory contents, and generated plot images. Dependencies are bash, cpufreq ondemand sysfs layout, root privileges, `cpufreq-bench`, and `cpufreq-bench_plot.sh`. Risks include obsolete governor paths on modern kernels, no cleanup/restore of original tunables, `eval` of generated commands, hard-coded CPU0 and `/var/log`, and failing if glob patterns match multiple/no logs unexpectedly. Test signals are dry-run review, root run on an ondemand-capable kernel, verification warning output, and plot generation for each parameter combination.

## Control Flow
Control flow is two nested loops in `measure()` followed by several nested plotting loops in `create_plots()`. State changes are direct sysfs writes to CPU0 ondemand tunables, benchmark log directory contents, and generated plot images. Dependencies are bash, cpufreq ondemand sysfs layout, root privileges, `cpufreq-bench`, and `cpufreq-bench_plot.sh`. Risks include obsolete governor paths on modern kernels, no cleanup/restore of original tunables, `eval` of generated commands, hard-coded CPU0 and `/var/log`, and failing if glob patterns match multiple/no logs unexpectedly. Test signals are dry-run review, root run on an ondemand-capable kernel, verification warning output, and plot generation for each parameter combination.

## State And Persistence
Control flow is two nested loops in `measure()` followed by several nested plotting loops in `create_plots()`. State changes are direct sysfs writes to CPU0 ondemand tunables, benchmark log directory contents, and generated plot images. Dependencies are bash, cpufreq ondemand sysfs layout, root privileges, `cpufreq-bench`, and `cpufreq-bench_plot.sh`. Risks include obsolete governor paths on modern kernels, no cleanup/restore of original tunables, `eval` of generated commands, hard-coded CPU0 and `/var/log`, and failing if glob patterns match multiple/no logs unexpectedly. Test signals are dry-run review, root run on an ondemand-capable kernel, verification warning output, and plot generation for each parameter combination.

## Dependencies And Integration Points
Control flow is two nested loops in `measure()` followed by several nested plotting loops in `create_plots()`. State changes are direct sysfs writes to CPU0 ondemand tunables, benchmark log directory contents, and generated plot images. Dependencies are bash, cpufreq ondemand sysfs layout, root privileges, `cpufreq-bench`, and `cpufreq-bench_plot.sh`. Risks include obsolete governor paths on modern kernels, no cleanup/restore of original tunables, `eval` of generated commands, hard-coded CPU0 and `/var/log`, and failing if glob patterns match multiple/no logs unexpectedly. Test signals are dry-run review, root run on an ondemand-capable kernel, verification warning output, and plot generation for each parameter combination.

## Risks And Edge Cases
Control flow is two nested loops in `measure()` followed by several nested plotting loops in `create_plots()`. State changes are direct sysfs writes to CPU0 ondemand tunables, benchmark log directory contents, and generated plot images. Dependencies are bash, cpufreq ondemand sysfs layout, root privileges, `cpufreq-bench`, and `cpufreq-bench_plot.sh`. Risks include obsolete governor paths on modern kernels, no cleanup/restore of original tunables, `eval` of generated commands, hard-coded CPU0 and `/var/log`, and failing if glob patterns match multiple/no logs unexpectedly. Test signals are dry-run review, root run on an ondemand-capable kernel, verification warning output, and plot generation for each parameter combination.

## Test Signals
Control flow is two nested loops in `measure()` followed by several nested plotting loops in `create_plots()`. State changes are direct sysfs writes to CPU0 ondemand tunables, benchmark log directory contents, and generated plot images. Dependencies are bash, cpufreq ondemand sysfs layout, root privileges, `cpufreq-bench`, and `cpufreq-bench_plot.sh`. Risks include obsolete governor paths on modern kernels, no cleanup/restore of original tunables, `eval` of generated commands, hard-coded CPU0 and `/var/log`, and failing if glob patterns match multiple/no logs unexpectedly. Test signals are dry-run review, root run on an ondemand-capable kernel, verification warning output, and plot generation for each parameter combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/cpufreq-bench_script.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/example.cfg -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bench/example.cfg

## Purpose
Example cpufreq-bench configuration file. It sets sleep/load times, CPU, priority, output directory, step increments, cycles, rounds, verbosity, and tested governor.

## Important APIs, Types, And Functions
The parser reads `key = value` pairs and applies them to `struct config`, so this file drives benchmark duration, CPU affinity, governor selection, and log destination. State effects occur when the benchmark runs: output under `/var/log/cpufreq-bench` and CPU governor changes. Dependencies are key names recognized by `parse.c` and a system with the configured governor. Risks include requiring root/write access for `/var/log` and governor changes, hard-coded CPU 0, and long runtime from cycles/rounds. Test signals are `cpufreq-bench -f example.cfg` parsing without errors and expected values in verbose startup output.

## Control Flow
The parser reads `key = value` pairs and applies them to `struct config`, so this file drives benchmark duration, CPU affinity, governor selection, and log destination. State effects occur when the benchmark runs: output under `/var/log/cpufreq-bench` and CPU governor changes. Dependencies are key names recognized by `parse.c` and a system with the configured governor. Risks include requiring root/write access for `/var/log` and governor changes, hard-coded CPU 0, and long runtime from cycles/rounds. Test signals are `cpufreq-bench -f example.cfg` parsing without errors and expected values in verbose startup output.

## State And Persistence
The parser reads `key = value` pairs and applies them to `struct config`, so this file drives benchmark duration, CPU affinity, governor selection, and log destination. State effects occur when the benchmark runs: output under `/var/log/cpufreq-bench` and CPU governor changes. Dependencies are key names recognized by `parse.c` and a system with the configured governor. Risks include requiring root/write access for `/var/log` and governor changes, hard-coded CPU 0, and long runtime from cycles/rounds. Test signals are `cpufreq-bench -f example.cfg` parsing without errors and expected values in verbose startup output.

## Dependencies And Integration Points
The parser reads `key = value` pairs and applies them to `struct config`, so this file drives benchmark duration, CPU affinity, governor selection, and log destination. State effects occur when the benchmark runs: output under `/var/log/cpufreq-bench` and CPU governor changes. Dependencies are key names recognized by `parse.c` and a system with the configured governor. Risks include requiring root/write access for `/var/log` and governor changes, hard-coded CPU 0, and long runtime from cycles/rounds. Test signals are `cpufreq-bench -f example.cfg` parsing without errors and expected values in verbose startup output.

## Risks And Edge Cases
The parser reads `key = value` pairs and applies them to `struct config`, so this file drives benchmark duration, CPU affinity, governor selection, and log destination. State effects occur when the benchmark runs: output under `/var/log/cpufreq-bench` and CPU governor changes. Dependencies are key names recognized by `parse.c` and a system with the configured governor. Risks include requiring root/write access for `/var/log` and governor changes, hard-coded CPU 0, and long runtime from cycles/rounds. Test signals are `cpufreq-bench -f example.cfg` parsing without errors and expected values in verbose startup output.

## Test Signals
The parser reads `key = value` pairs and applies them to `struct config`, so this file drives benchmark duration, CPU affinity, governor selection, and log destination. State effects occur when the benchmark runs: output under `/var/log/cpufreq-bench` and CPU governor changes. Dependencies are key names recognized by `parse.c` and a system with the configured governor. Risks include requiring root/write access for `/var/log` and governor changes, hard-coded CPU 0, and long runtime from cycles/rounds. Test signals are `cpufreq-bench -f example.cfg` parsing without errors and expected values in verbose startup output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/example.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/main.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bench/main.c

## Purpose
CLI entry point for cpufreq-bench. It creates a default config, parses command-line overrides for timing, CPU, governor, priority, config file, output, cycles/rounds, and verbosity, prepares the process/system, runs the benchmark, and frees resources.

## Important APIs, Types, And Functions
Control flow is `prepare_default_config()`, `getopt_long()` loop applying overrides, optional verbose parameter print, `prepare_user()`, `prepare_system()`, `start_benchmark()`, output close, and config free. State includes the mutable `struct config`, output file handle, scheduler/affinity/governor changes, and logs. Dependencies are `parse.c`, `system.c`, `benchmark.c`, getopt, and libcpupower sysfs writes. Risks include minimal validation of numeric `sscanf()` results, `strncpy(config->governor, optarg, 14)` without guaranteed NUL on long input, early returns leaking config/output in some paths, and no original governor restore. Test signals are help, invalid priority, config-file override order, output directory creation, and short benchmark execution.

## Control Flow
Control flow is `prepare_default_config()`, `getopt_long()` loop applying overrides, optional verbose parameter print, `prepare_user()`, `prepare_system()`, `start_benchmark()`, output close, and config free. State includes the mutable `struct config`, output file handle, scheduler/affinity/governor changes, and logs. Dependencies are `parse.c`, `system.c`, `benchmark.c`, getopt, and libcpupower sysfs writes. Risks include minimal validation of numeric `sscanf()` results, `strncpy(config->governor, optarg, 14)` without guaranteed NUL on long input, early returns leaking config/output in some paths, and no original governor restore. Test signals are help, invalid priority, config-file override order, output directory creation, and short benchmark execution.

## State And Persistence
Control flow is `prepare_default_config()`, `getopt_long()` loop applying overrides, optional verbose parameter print, `prepare_user()`, `prepare_system()`, `start_benchmark()`, output close, and config free. State includes the mutable `struct config`, output file handle, scheduler/affinity/governor changes, and logs. Dependencies are `parse.c`, `system.c`, `benchmark.c`, getopt, and libcpupower sysfs writes. Risks include minimal validation of numeric `sscanf()` results, `strncpy(config->governor, optarg, 14)` without guaranteed NUL on long input, early returns leaking config/output in some paths, and no original governor restore. Test signals are help, invalid priority, config-file override order, output directory creation, and short benchmark execution.

## Dependencies And Integration Points
Control flow is `prepare_default_config()`, `getopt_long()` loop applying overrides, optional verbose parameter print, `prepare_user()`, `prepare_system()`, `start_benchmark()`, output close, and config free. State includes the mutable `struct config`, output file handle, scheduler/affinity/governor changes, and logs. Dependencies are `parse.c`, `system.c`, `benchmark.c`, getopt, and libcpupower sysfs writes. Risks include minimal validation of numeric `sscanf()` results, `strncpy(config->governor, optarg, 14)` without guaranteed NUL on long input, early returns leaking config/output in some paths, and no original governor restore. Test signals are help, invalid priority, config-file override order, output directory creation, and short benchmark execution.

## Risks And Edge Cases
Control flow is `prepare_default_config()`, `getopt_long()` loop applying overrides, optional verbose parameter print, `prepare_user()`, `prepare_system()`, `start_benchmark()`, output close, and config free. State includes the mutable `struct config`, output file handle, scheduler/affinity/governor changes, and logs. Dependencies are `parse.c`, `system.c`, `benchmark.c`, getopt, and libcpupower sysfs writes. Risks include minimal validation of numeric `sscanf()` results, `strncpy(config->governor, optarg, 14)` without guaranteed NUL on long input, early returns leaking config/output in some paths, and no original governor restore. Test signals are help, invalid priority, config-file override order, output directory creation, and short benchmark execution.

## Test Signals
Control flow is `prepare_default_config()`, `getopt_long()` loop applying overrides, optional verbose parameter print, `prepare_user()`, `prepare_system()`, `start_benchmark()`, output close, and config free. State includes the mutable `struct config`, output file handle, scheduler/affinity/governor changes, and logs. Dependencies are `parse.c`, `system.c`, `benchmark.c`, getopt, and libcpupower sysfs writes. Risks include minimal validation of numeric `sscanf()` results, `strncpy(config->governor, optarg, 14)` without guaranteed NUL on long input, early returns leaking config/output in some paths, and no original governor restore. Test signals are help, invalid priority, config-file override order, output directory creation, and short benchmark execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/parse.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bench/parse.c

## Purpose
Configuration and output-file support for cpufreq-bench. It converts priority strings, creates timestamped log files, allocates default configs, and parses simple config files.

## Important APIs, Types, And Functions
`prepare_output()` creates the output directory if needed, builds a filename using hostname/kernel release/time, opens it, and writes the header. `prepare_default_config()` initializes defaults then optionally loads `DEFAULT_CONFIG_FILE`. `prepare_config()` reads lines, ignores comments/blanks, parses `opt = val`, and updates recognized fields. State includes allocated config memory, output file handles, generated log files, and parsed values. Dependencies are libc file APIs, `uname()`, directory APIs, `config.h`, and `parse.h`. Risks include calling `closedir(dir)` even when `opendir()` failed and `mkdir()` succeeded without reopening, freeing `config` inside `prepare_config()` on open failure despite caller ownership, leaking/overwriting previous output handles, and weak numeric validation. Test signals are default config load, nonexistent config file, output directory creation, comments/unknown keys, priority prefixes, and ASAN for ownership bugs.

## Control Flow
`prepare_output()` creates the output directory if needed, builds a filename using hostname/kernel release/time, opens it, and writes the header. `prepare_default_config()` initializes defaults then optionally loads `DEFAULT_CONFIG_FILE`. `prepare_config()` reads lines, ignores comments/blanks, parses `opt = val`, and updates recognized fields. State includes allocated config memory, output file handles, generated log files, and parsed values. Dependencies are libc file APIs, `uname()`, directory APIs, `config.h`, and `parse.h`. Risks include calling `closedir(dir)` even when `opendir()` failed and `mkdir()` succeeded without reopening, freeing `config` inside `prepare_config()` on open failure despite caller ownership, leaking/overwriting previous output handles, and weak numeric validation. Test signals are default config load, nonexistent config file, output directory creation, comments/unknown keys, priority prefixes, and ASAN for ownership bugs.

## State And Persistence
`prepare_output()` creates the output directory if needed, builds a filename using hostname/kernel release/time, opens it, and writes the header. `prepare_default_config()` initializes defaults then optionally loads `DEFAULT_CONFIG_FILE`. `prepare_config()` reads lines, ignores comments/blanks, parses `opt = val`, and updates recognized fields. State includes allocated config memory, output file handles, generated log files, and parsed values. Dependencies are libc file APIs, `uname()`, directory APIs, `config.h`, and `parse.h`. Risks include calling `closedir(dir)` even when `opendir()` failed and `mkdir()` succeeded without reopening, freeing `config` inside `prepare_config()` on open failure despite caller ownership, leaking/overwriting previous output handles, and weak numeric validation. Test signals are default config load, nonexistent config file, output directory creation, comments/unknown keys, priority prefixes, and ASAN for ownership bugs.

## Dependencies And Integration Points
`prepare_output()` creates the output directory if needed, builds a filename using hostname/kernel release/time, opens it, and writes the header. `prepare_default_config()` initializes defaults then optionally loads `DEFAULT_CONFIG_FILE`. `prepare_config()` reads lines, ignores comments/blanks, parses `opt = val`, and updates recognized fields. State includes allocated config memory, output file handles, generated log files, and parsed values. Dependencies are libc file APIs, `uname()`, directory APIs, `config.h`, and `parse.h`. Risks include calling `closedir(dir)` even when `opendir()` failed and `mkdir()` succeeded without reopening, freeing `config` inside `prepare_config()` on open failure despite caller ownership, leaking/overwriting previous output handles, and weak numeric validation. Test signals are default config load, nonexistent config file, output directory creation, comments/unknown keys, priority prefixes, and ASAN for ownership bugs.

## Risks And Edge Cases
`prepare_output()` creates the output directory if needed, builds a filename using hostname/kernel release/time, opens it, and writes the header. `prepare_default_config()` initializes defaults then optionally loads `DEFAULT_CONFIG_FILE`. `prepare_config()` reads lines, ignores comments/blanks, parses `opt = val`, and updates recognized fields. State includes allocated config memory, output file handles, generated log files, and parsed values. Dependencies are libc file APIs, `uname()`, directory APIs, `config.h`, and `parse.h`. Risks include calling `closedir(dir)` even when `opendir()` failed and `mkdir()` succeeded without reopening, freeing `config` inside `prepare_config()` on open failure despite caller ownership, leaking/overwriting previous output handles, and weak numeric validation. Test signals are default config load, nonexistent config file, output directory creation, comments/unknown keys, priority prefixes, and ASAN for ownership bugs.

## Test Signals
`prepare_output()` creates the output directory if needed, builds a filename using hostname/kernel release/time, opens it, and writes the header. `prepare_default_config()` initializes defaults then optionally loads `DEFAULT_CONFIG_FILE`. `prepare_config()` reads lines, ignores comments/blanks, parses `opt = val`, and updates recognized fields. State includes allocated config memory, output file handles, generated log files, and parsed values. Dependencies are libc file APIs, `uname()`, directory APIs, `config.h`, and `parse.h`. Risks include calling `closedir(dir)` even when `opendir()` failed and `mkdir()` succeeded without reopening, freeing `config` inside `prepare_config()` on open failure despite caller ownership, leaking/overwriting previous output handles, and weak numeric validation. Test signals are default config load, nonexistent config file, output directory creation, comments/unknown keys, priority prefixes, and ASAN for ownership bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/parse.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bench/parse.h

## Purpose
Defines cpufreq-bench runtime configuration and parser API. `struct config` stores sleep/load timings, steps, cycle/round counts, target CPU, governor name, scheduler priority enum, verbosity, output handle, and an optional output filename pointer.

## Important APIs, Types, And Functions
State is owned by callers that allocate through `prepare_default_config()` and eventually free the struct and close output if needed. Dependencies are `FILE` being declared by including stdio before this header in users, and parser implementations in `parse.c`. Risks include missing include guards, a fixed 15-byte governor buffer, comments promising `output_filename` ownership while implementation does not consistently set it, and header reliance on include order for `FILE`. Test signals are compiler warnings with strict include ordering, long governor names, and config lifetime checks.

## Control Flow
State is owned by callers that allocate through `prepare_default_config()` and eventually free the struct and close output if needed. Dependencies are `FILE` being declared by including stdio before this header in users, and parser implementations in `parse.c`. Risks include missing include guards, a fixed 15-byte governor buffer, comments promising `output_filename` ownership while implementation does not consistently set it, and header reliance on include order for `FILE`. Test signals are compiler warnings with strict include ordering, long governor names, and config lifetime checks.

## State And Persistence
State is owned by callers that allocate through `prepare_default_config()` and eventually free the struct and close output if needed. Dependencies are `FILE` being declared by including stdio before this header in users, and parser implementations in `parse.c`. Risks include missing include guards, a fixed 15-byte governor buffer, comments promising `output_filename` ownership while implementation does not consistently set it, and header reliance on include order for `FILE`. Test signals are compiler warnings with strict include ordering, long governor names, and config lifetime checks.

## Dependencies And Integration Points
State is owned by callers that allocate through `prepare_default_config()` and eventually free the struct and close output if needed. Dependencies are `FILE` being declared by including stdio before this header in users, and parser implementations in `parse.c`. Risks include missing include guards, a fixed 15-byte governor buffer, comments promising `output_filename` ownership while implementation does not consistently set it, and header reliance on include order for `FILE`. Test signals are compiler warnings with strict include ordering, long governor names, and config lifetime checks.

## Risks And Edge Cases
State is owned by callers that allocate through `prepare_default_config()` and eventually free the struct and close output if needed. Dependencies are `FILE` being declared by including stdio before this header in users, and parser implementations in `parse.c`. Risks include missing include guards, a fixed 15-byte governor buffer, comments promising `output_filename` ownership while implementation does not consistently set it, and header reliance on include order for `FILE`. Test signals are compiler warnings with strict include ordering, long governor names, and config lifetime checks.

## Test Signals
State is owned by callers that allocate through `prepare_default_config()` and eventually free the struct and close output if needed. Dependencies are `FILE` being declared by including stdio before this header in users, and parser implementations in `parse.c`. Risks include missing include guards, a fixed 15-byte governor buffer, comments promising `output_filename` ownership while implementation does not consistently set it, and header reliance on include order for `FILE`. Test signals are compiler warnings with strict include ordering, long governor names, and config lifetime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/parse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/system.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bench/system.c

## Purpose
System interaction layer for cpufreq-bench. It provides microsecond wall-clock timing, cpufreq governor changes, CPU affinity, scheduler priority changes, runtime-duration estimation, and setup of process/system state before the benchmark loop.

## Important APIs, Types, And Functions
Control flow uses `gettimeofday()` for `get_time()`, `cpupower_is_cpu_online()` plus `cpufreq_modify_policy_governor()` for governor changes, `sched_setaffinity()` for CPU pinning, `sched_setscheduler()` for priority, and switch logic over configured priority. State changes affect the running process and kernel cpufreq sysfs policy. Dependencies are libcpupower headers/libraries, scheduler APIs, and sysfs. Risks include warnings but continued benchmark after affinity/priority failures, `SCHED_OTHER` ignoring nonzero priorities on many systems, no governor restoration, and duration estimate arithmetic inaccuracies. Test signals are CPU online/offline cases, permission failure for scheduler/governor, affinity checks, and verbose setup output.

## Control Flow
Control flow uses `gettimeofday()` for `get_time()`, `cpupower_is_cpu_online()` plus `cpufreq_modify_policy_governor()` for governor changes, `sched_setaffinity()` for CPU pinning, `sched_setscheduler()` for priority, and switch logic over configured priority. State changes affect the running process and kernel cpufreq sysfs policy. Dependencies are libcpupower headers/libraries, scheduler APIs, and sysfs. Risks include warnings but continued benchmark after affinity/priority failures, `SCHED_OTHER` ignoring nonzero priorities on many systems, no governor restoration, and duration estimate arithmetic inaccuracies. Test signals are CPU online/offline cases, permission failure for scheduler/governor, affinity checks, and verbose setup output.

## State And Persistence
Control flow uses `gettimeofday()` for `get_time()`, `cpupower_is_cpu_online()` plus `cpufreq_modify_policy_governor()` for governor changes, `sched_setaffinity()` for CPU pinning, `sched_setscheduler()` for priority, and switch logic over configured priority. State changes affect the running process and kernel cpufreq sysfs policy. Dependencies are libcpupower headers/libraries, scheduler APIs, and sysfs. Risks include warnings but continued benchmark after affinity/priority failures, `SCHED_OTHER` ignoring nonzero priorities on many systems, no governor restoration, and duration estimate arithmetic inaccuracies. Test signals are CPU online/offline cases, permission failure for scheduler/governor, affinity checks, and verbose setup output.

## Dependencies And Integration Points
Control flow uses `gettimeofday()` for `get_time()`, `cpupower_is_cpu_online()` plus `cpufreq_modify_policy_governor()` for governor changes, `sched_setaffinity()` for CPU pinning, `sched_setscheduler()` for priority, and switch logic over configured priority. State changes affect the running process and kernel cpufreq sysfs policy. Dependencies are libcpupower headers/libraries, scheduler APIs, and sysfs. Risks include warnings but continued benchmark after affinity/priority failures, `SCHED_OTHER` ignoring nonzero priorities on many systems, no governor restoration, and duration estimate arithmetic inaccuracies. Test signals are CPU online/offline cases, permission failure for scheduler/governor, affinity checks, and verbose setup output.

## Risks And Edge Cases
Control flow uses `gettimeofday()` for `get_time()`, `cpupower_is_cpu_online()` plus `cpufreq_modify_policy_governor()` for governor changes, `sched_setaffinity()` for CPU pinning, `sched_setscheduler()` for priority, and switch logic over configured priority. State changes affect the running process and kernel cpufreq sysfs policy. Dependencies are libcpupower headers/libraries, scheduler APIs, and sysfs. Risks include warnings but continued benchmark after affinity/priority failures, `SCHED_OTHER` ignoring nonzero priorities on many systems, no governor restoration, and duration estimate arithmetic inaccuracies. Test signals are CPU online/offline cases, permission failure for scheduler/governor, affinity checks, and verbose setup output.

## Test Signals
Control flow uses `gettimeofday()` for `get_time()`, `cpupower_is_cpu_online()` plus `cpufreq_modify_policy_governor()` for governor changes, `sched_setaffinity()` for CPU pinning, `sched_setscheduler()` for priority, and switch logic over configured priority. State changes affect the running process and kernel cpufreq sysfs policy. Dependencies are libcpupower headers/libraries, scheduler APIs, and sysfs. Risks include warnings but continued benchmark after affinity/priority failures, `SCHED_OTHER` ignoring nonzero priorities on many systems, no governor restoration, and duration estimate arithmetic inaccuracies. Test signals are CPU online/offline cases, permission failure for scheduler/governor, affinity checks, and verbose setup output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/system.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/system.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bench/system.h

## Purpose
Declares cpufreq-bench system helper functions and includes `parse.h` for `struct config`. It exposes timing, governor/affinity/priority setters, and user/system preparation routines.

## Important APIs, Types, And Functions
There is no runtime control flow or state in the header. Dependencies are `parse.h` and the implementations in `system.c`. Risks include no include guard, `get_time()` declaration missing an explicit `int`-free prototype style distinction from implementation `long long int`, and exposing setters that mutate global process/kernel state without documenting restoration. Test signals are strict compiler warnings and successful linkage from `main.c`/`benchmark.c`.

## Control Flow
There is no runtime control flow or state in the header. Dependencies are `parse.h` and the implementations in `system.c`. Risks include no include guard, `get_time()` declaration missing an explicit `int`-free prototype style distinction from implementation `long long int`, and exposing setters that mutate global process/kernel state without documenting restoration. Test signals are strict compiler warnings and successful linkage from `main.c`/`benchmark.c`.

## State And Persistence
There is no runtime control flow or state in the header. Dependencies are `parse.h` and the implementations in `system.c`. Risks include no include guard, `get_time()` declaration missing an explicit `int`-free prototype style distinction from implementation `long long int`, and exposing setters that mutate global process/kernel state without documenting restoration. Test signals are strict compiler warnings and successful linkage from `main.c`/`benchmark.c`.

## Dependencies And Integration Points
There is no runtime control flow or state in the header. Dependencies are `parse.h` and the implementations in `system.c`. Risks include no include guard, `get_time()` declaration missing an explicit `int`-free prototype style distinction from implementation `long long int`, and exposing setters that mutate global process/kernel state without documenting restoration. Test signals are strict compiler warnings and successful linkage from `main.c`/`benchmark.c`.

## Risks And Edge Cases
There is no runtime control flow or state in the header. Dependencies are `parse.h` and the implementations in `system.c`. Risks include no include guard, `get_time()` declaration missing an explicit `int`-free prototype style distinction from implementation `long long int`, and exposing setters that mutate global process/kernel state without documenting restoration. Test signals are strict compiler warnings and successful linkage from `main.c`/`benchmark.c`.

## Test Signals
There is no runtime control flow or state in the header. Dependencies are `parse.h` and the implementations in `system.c`. Risks include no include guard, `get_time()` declaration missing an explicit `int`-free prototype style distinction from implementation `long long int`, and exposing setters that mutate global process/kernel state without documenting restoration. Test signals are strict compiler warnings and successful linkage from `main.c`/`benchmark.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/system.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bindings/python/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bindings/python/Makefile

## Purpose
Build rules for raw SWIG Python bindings to libcpupower. It detects `swig` and `python-config`, generates `raw_pylibcpupower_wrap.c` from `.swg`, compiles a PIC wrapper object, links `_raw_pylibcpupower.so`, and installs the extension plus generated Python module into Python site-packages.

## Important APIs, Types, And Functions
State is generated SWIG C/Python files, wrapper object, shared object, and installed site-packages files. Dependencies are a previously installed libcpupower, SWIG, Python development config, compiler, and `python3 -c import site`. Risks include using `python-config` while install path uses `python3`, default `LDFLAGS=-lcpupower` relying on library search paths, direct install into system site-packages, and no versioned wheel/packaging metadata. Test signals are missing-tool error messages, `make`, import of `raw_pylibcpupower`, and install/uninstall under a staged `INSTALL_DIR`.

## Control Flow
State is generated SWIG C/Python files, wrapper object, shared object, and installed site-packages files. Dependencies are a previously installed libcpupower, SWIG, Python development config, compiler, and `python3 -c import site`. Risks include using `python-config` while install path uses `python3`, default `LDFLAGS=-lcpupower` relying on library search paths, direct install into system site-packages, and no versioned wheel/packaging metadata. Test signals are missing-tool error messages, `make`, import of `raw_pylibcpupower`, and install/uninstall under a staged `INSTALL_DIR`.

## State And Persistence
State is generated SWIG C/Python files, wrapper object, shared object, and installed site-packages files. Dependencies are a previously installed libcpupower, SWIG, Python development config, compiler, and `python3 -c import site`. Risks include using `python-config` while install path uses `python3`, default `LDFLAGS=-lcpupower` relying on library search paths, direct install into system site-packages, and no versioned wheel/packaging metadata. Test signals are missing-tool error messages, `make`, import of `raw_pylibcpupower`, and install/uninstall under a staged `INSTALL_DIR`.

## Dependencies And Integration Points
State is generated SWIG C/Python files, wrapper object, shared object, and installed site-packages files. Dependencies are a previously installed libcpupower, SWIG, Python development config, compiler, and `python3 -c import site`. Risks include using `python-config` while install path uses `python3`, default `LDFLAGS=-lcpupower` relying on library search paths, direct install into system site-packages, and no versioned wheel/packaging metadata. Test signals are missing-tool error messages, `make`, import of `raw_pylibcpupower`, and install/uninstall under a staged `INSTALL_DIR`.

## Risks And Edge Cases
State is generated SWIG C/Python files, wrapper object, shared object, and installed site-packages files. Dependencies are a previously installed libcpupower, SWIG, Python development config, compiler, and `python3 -c import site`. Risks include using `python-config` while install path uses `python3`, default `LDFLAGS=-lcpupower` relying on library search paths, direct install into system site-packages, and no versioned wheel/packaging metadata. Test signals are missing-tool error messages, `make`, import of `raw_pylibcpupower`, and install/uninstall under a staged `INSTALL_DIR`.

## Test Signals
State is generated SWIG C/Python files, wrapper object, shared object, and installed site-packages files. Dependencies are a previously installed libcpupower, SWIG, Python development config, compiler, and `python3 -c import site`. Risks include using `python-config` while install path uses `python3`, default `LDFLAGS=-lcpupower` relying on library search paths, direct install into system site-packages, and no versioned wheel/packaging metadata. Test signals are missing-tool error messages, `make`, import of `raw_pylibcpupower`, and install/uninstall under a staged `INSTALL_DIR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bindings/python/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bindings/python/test_raw_pylibcpupower.py -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bindings/python/test_raw_pylibcpupower.py

## Purpose
Smoke-test script for the raw Python libcpupower bindings. It calls cpuidle state count, attempts to disable CPU0 C-state 0, checks whether it is disabled, and exercises pointer-style topology allocation/access.

## Important APIs, Types, And Functions
Control flow imports `raw_pylibcpupower`, prints results for each call, and uses Python `match` to decode documented return values. State may be changed by `cpuidle_state_disable(0, 0, 1)`, which can disable an idle state if run with permission. Dependencies are Python 3.10+ for `match`, installed raw bindings, sysfs cpuidle support, and possibly root. Risks include mutating CPU idle policy without restoring it, assuming CPU0/state0 exists, virtual machine failures, and no assertions/exit status for automated testing. Test signals are successful import, expected negative returns without privilege, topology count greater than zero, and manual restoration of C-state when needed.

## Control Flow
Control flow imports `raw_pylibcpupower`, prints results for each call, and uses Python `match` to decode documented return values. State may be changed by `cpuidle_state_disable(0, 0, 1)`, which can disable an idle state if run with permission. Dependencies are Python 3.10+ for `match`, installed raw bindings, sysfs cpuidle support, and possibly root. Risks include mutating CPU idle policy without restoring it, assuming CPU0/state0 exists, virtual machine failures, and no assertions/exit status for automated testing. Test signals are successful import, expected negative returns without privilege, topology count greater than zero, and manual restoration of C-state when needed.

## State And Persistence
Control flow imports `raw_pylibcpupower`, prints results for each call, and uses Python `match` to decode documented return values. State may be changed by `cpuidle_state_disable(0, 0, 1)`, which can disable an idle state if run with permission. Dependencies are Python 3.10+ for `match`, installed raw bindings, sysfs cpuidle support, and possibly root. Risks include mutating CPU idle policy without restoring it, assuming CPU0/state0 exists, virtual machine failures, and no assertions/exit status for automated testing. Test signals are successful import, expected negative returns without privilege, topology count greater than zero, and manual restoration of C-state when needed.

## Dependencies And Integration Points
Control flow imports `raw_pylibcpupower`, prints results for each call, and uses Python `match` to decode documented return values. State may be changed by `cpuidle_state_disable(0, 0, 1)`, which can disable an idle state if run with permission. Dependencies are Python 3.10+ for `match`, installed raw bindings, sysfs cpuidle support, and possibly root. Risks include mutating CPU idle policy without restoring it, assuming CPU0/state0 exists, virtual machine failures, and no assertions/exit status for automated testing. Test signals are successful import, expected negative returns without privilege, topology count greater than zero, and manual restoration of C-state when needed.

## Risks And Edge Cases
Control flow imports `raw_pylibcpupower`, prints results for each call, and uses Python `match` to decode documented return values. State may be changed by `cpuidle_state_disable(0, 0, 1)`, which can disable an idle state if run with permission. Dependencies are Python 3.10+ for `match`, installed raw bindings, sysfs cpuidle support, and possibly root. Risks include mutating CPU idle policy without restoring it, assuming CPU0/state0 exists, virtual machine failures, and no assertions/exit status for automated testing. Test signals are successful import, expected negative returns without privilege, topology count greater than zero, and manual restoration of C-state when needed.

## Test Signals
Control flow imports `raw_pylibcpupower`, prints results for each call, and uses Python `match` to decode documented return values. State may be changed by `cpuidle_state_disable(0, 0, 1)`, which can disable an idle state if run with permission. Dependencies are Python 3.10+ for `match`, installed raw bindings, sysfs cpuidle support, and possibly root. Risks include mutating CPU idle policy without restoring it, assuming CPU0/state0 exists, virtual machine failures, and no assertions/exit status for automated testing. Test signals are successful import, expected negative returns without privilege, topology count greater than zero, and manual restoration of C-state when needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bindings/python/test_raw_pylibcpupower.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/cpupower-completion.sh -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/cpupower-completion.sh

## Purpose
Bash completion script for the `cpupower` CLI. It completes top-level subcommands, help/version/cpu selector options, and subcommand-specific flags and values such as available governors/frequencies from sysfs.

## Important APIs, Types, And Functions
Control flow is a set of completion functions selected by `_cpupower()` based on the first command word or `-c/--cpu` context. State is bash `COMPREPLY` only. Dependencies are bash completion APIs, `compgen`, cpupower subcommand names, and `/sys/devices/system/cpu/cpufreq` policy files for dynamic completions. Risks include stale option lists as cpupower changes, fragile parsing of command position, unquoted sysfs command substitutions, and only sampling the first policy's governors/frequencies. Test signals are sourcing in bash, completing each subcommand, systems with and without cpufreq sysfs, and completion after `cpupower -c 1`.

## Control Flow
Control flow is a set of completion functions selected by `_cpupower()` based on the first command word or `-c/--cpu` context. State is bash `COMPREPLY` only. Dependencies are bash completion APIs, `compgen`, cpupower subcommand names, and `/sys/devices/system/cpu/cpufreq` policy files for dynamic completions. Risks include stale option lists as cpupower changes, fragile parsing of command position, unquoted sysfs command substitutions, and only sampling the first policy's governors/frequencies. Test signals are sourcing in bash, completing each subcommand, systems with and without cpufreq sysfs, and completion after `cpupower -c 1`.

## State And Persistence
Control flow is a set of completion functions selected by `_cpupower()` based on the first command word or `-c/--cpu` context. State is bash `COMPREPLY` only. Dependencies are bash completion APIs, `compgen`, cpupower subcommand names, and `/sys/devices/system/cpu/cpufreq` policy files for dynamic completions. Risks include stale option lists as cpupower changes, fragile parsing of command position, unquoted sysfs command substitutions, and only sampling the first policy's governors/frequencies. Test signals are sourcing in bash, completing each subcommand, systems with and without cpufreq sysfs, and completion after `cpupower -c 1`.

## Dependencies And Integration Points
Control flow is a set of completion functions selected by `_cpupower()` based on the first command word or `-c/--cpu` context. State is bash `COMPREPLY` only. Dependencies are bash completion APIs, `compgen`, cpupower subcommand names, and `/sys/devices/system/cpu/cpufreq` policy files for dynamic completions. Risks include stale option lists as cpupower changes, fragile parsing of command position, unquoted sysfs command substitutions, and only sampling the first policy's governors/frequencies. Test signals are sourcing in bash, completing each subcommand, systems with and without cpufreq sysfs, and completion after `cpupower -c 1`.

## Risks And Edge Cases
Control flow is a set of completion functions selected by `_cpupower()` based on the first command word or `-c/--cpu` context. State is bash `COMPREPLY` only. Dependencies are bash completion APIs, `compgen`, cpupower subcommand names, and `/sys/devices/system/cpu/cpufreq` policy files for dynamic completions. Risks include stale option lists as cpupower changes, fragile parsing of command position, unquoted sysfs command substitutions, and only sampling the first policy's governors/frequencies. Test signals are sourcing in bash, completing each subcommand, systems with and without cpufreq sysfs, and completion after `cpupower -c 1`.

## Test Signals
Control flow is a set of completion functions selected by `_cpupower()` based on the first command word or `-c/--cpu` context. State is bash `COMPREPLY` only. Dependencies are bash completion APIs, `compgen`, cpupower subcommand names, and `/sys/devices/system/cpu/cpufreq` policy files for dynamic completions. Risks include stale option lists as cpupower changes, fragile parsing of command position, unquoted sysfs command substitutions, and only sampling the first policy's governors/frequencies. Test signals are sourcing in bash, completing each subcommand, systems with and without cpufreq sysfs, and completion after `cpupower -c 1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/cpupower-completion.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/cpupower-service.conf -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/cpupower-service.conf

## Purpose
Default commented configuration for the cpupower systemd service wrapper. It documents optional environment variables for governor, min/max/fixed frequency, Intel performance bias, and energy performance preference.

## Important APIs, Types, And Functions
There is no executable control flow; when installed, systemd reads it as an optional `EnvironmentFile`, and `cpupower.sh` consumes variables such as `GOVERNOR`, `MIN_FREQ`, `MAX_FREQ`, `FREQ`, `PERF_BIAS`, and `EPP`. State changes happen only if an administrator uncomments values and enables the service. Dependencies are systemd environment-file syntax and cpupower command support for the selected options. Risks include invalid values causing boot-time service failure, comments mentioning specific governors not present on all kernels, and direct policy changes at boot. Test signals are shellcheck-like syntax checks, service run with each variable, and systemd journal exit status.

## Control Flow
There is no executable control flow; when installed, systemd reads it as an optional `EnvironmentFile`, and `cpupower.sh` consumes variables such as `GOVERNOR`, `MIN_FREQ`, `MAX_FREQ`, `FREQ`, `PERF_BIAS`, and `EPP`. State changes happen only if an administrator uncomments values and enables the service. Dependencies are systemd environment-file syntax and cpupower command support for the selected options. Risks include invalid values causing boot-time service failure, comments mentioning specific governors not present on all kernels, and direct policy changes at boot. Test signals are shellcheck-like syntax checks, service run with each variable, and systemd journal exit status.

## State And Persistence
There is no executable control flow; when installed, systemd reads it as an optional `EnvironmentFile`, and `cpupower.sh` consumes variables such as `GOVERNOR`, `MIN_FREQ`, `MAX_FREQ`, `FREQ`, `PERF_BIAS`, and `EPP`. State changes happen only if an administrator uncomments values and enables the service. Dependencies are systemd environment-file syntax and cpupower command support for the selected options. Risks include invalid values causing boot-time service failure, comments mentioning specific governors not present on all kernels, and direct policy changes at boot. Test signals are shellcheck-like syntax checks, service run with each variable, and systemd journal exit status.

## Dependencies And Integration Points
There is no executable control flow; when installed, systemd reads it as an optional `EnvironmentFile`, and `cpupower.sh` consumes variables such as `GOVERNOR`, `MIN_FREQ`, `MAX_FREQ`, `FREQ`, `PERF_BIAS`, and `EPP`. State changes happen only if an administrator uncomments values and enables the service. Dependencies are systemd environment-file syntax and cpupower command support for the selected options. Risks include invalid values causing boot-time service failure, comments mentioning specific governors not present on all kernels, and direct policy changes at boot. Test signals are shellcheck-like syntax checks, service run with each variable, and systemd journal exit status.

## Risks And Edge Cases
There is no executable control flow; when installed, systemd reads it as an optional `EnvironmentFile`, and `cpupower.sh` consumes variables such as `GOVERNOR`, `MIN_FREQ`, `MAX_FREQ`, `FREQ`, `PERF_BIAS`, and `EPP`. State changes happen only if an administrator uncomments values and enables the service. Dependencies are systemd environment-file syntax and cpupower command support for the selected options. Risks include invalid values causing boot-time service failure, comments mentioning specific governors not present on all kernels, and direct policy changes at boot. Test signals are shellcheck-like syntax checks, service run with each variable, and systemd journal exit status.

## Test Signals
There is no executable control flow; when installed, systemd reads it as an optional `EnvironmentFile`, and `cpupower.sh` consumes variables such as `GOVERNOR`, `MIN_FREQ`, `MAX_FREQ`, `FREQ`, `PERF_BIAS`, and `EPP`. State changes happen only if an administrator uncomments values and enables the service. Dependencies are systemd environment-file syntax and cpupower command support for the selected options. Risks include invalid values causing boot-time service failure, comments mentioning specific governors not present on all kernels, and direct policy changes at boot. Test signals are shellcheck-like syntax checks, service run with each variable, and systemd journal exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/cpupower-service.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/cpupower.service.in -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/cpupower.service.in

## Purpose
Template for a systemd oneshot unit that applies cpupower configuration at boot. Install rules substitute `___CDIR___` with the config directory and `___LDIR___` with the libexec directory.

## Important APIs, Types, And Functions
Control flow is systemd-managed: skip in containers via `ConditionVirtualization=!container`, load optional environment file, execute the wrapper script once, and remain active after exit. State is systemd unit activation state and any CPU policy changes made by the wrapper. Dependencies are systemd, installed config file, installed libexec wrapper, and cpupower binary on PATH. Risks include path substitution errors, service reporting failed when one configured command fails, no automatic reapply after CPU hotplug, and container condition not covering all virtualized environments. Test signals are rendered unit inspection, `systemd-analyze verify`, and staged service execution with a temporary config.

## Control Flow
Control flow is systemd-managed: skip in containers via `ConditionVirtualization=!container`, load optional environment file, execute the wrapper script once, and remain active after exit. State is systemd unit activation state and any CPU policy changes made by the wrapper. Dependencies are systemd, installed config file, installed libexec wrapper, and cpupower binary on PATH. Risks include path substitution errors, service reporting failed when one configured command fails, no automatic reapply after CPU hotplug, and container condition not covering all virtualized environments. Test signals are rendered unit inspection, `systemd-analyze verify`, and staged service execution with a temporary config.

## State And Persistence
Control flow is systemd-managed: skip in containers via `ConditionVirtualization=!container`, load optional environment file, execute the wrapper script once, and remain active after exit. State is systemd unit activation state and any CPU policy changes made by the wrapper. Dependencies are systemd, installed config file, installed libexec wrapper, and cpupower binary on PATH. Risks include path substitution errors, service reporting failed when one configured command fails, no automatic reapply after CPU hotplug, and container condition not covering all virtualized environments. Test signals are rendered unit inspection, `systemd-analyze verify`, and staged service execution with a temporary config.

## Dependencies And Integration Points
Control flow is systemd-managed: skip in containers via `ConditionVirtualization=!container`, load optional environment file, execute the wrapper script once, and remain active after exit. State is systemd unit activation state and any CPU policy changes made by the wrapper. Dependencies are systemd, installed config file, installed libexec wrapper, and cpupower binary on PATH. Risks include path substitution errors, service reporting failed when one configured command fails, no automatic reapply after CPU hotplug, and container condition not covering all virtualized environments. Test signals are rendered unit inspection, `systemd-analyze verify`, and staged service execution with a temporary config.

## Risks And Edge Cases
Control flow is systemd-managed: skip in containers via `ConditionVirtualization=!container`, load optional environment file, execute the wrapper script once, and remain active after exit. State is systemd unit activation state and any CPU policy changes made by the wrapper. Dependencies are systemd, installed config file, installed libexec wrapper, and cpupower binary on PATH. Risks include path substitution errors, service reporting failed when one configured command fails, no automatic reapply after CPU hotplug, and container condition not covering all virtualized environments. Test signals are rendered unit inspection, `systemd-analyze verify`, and staged service execution with a temporary config.

## Test Signals
Control flow is systemd-managed: skip in containers via `ConditionVirtualization=!container`, load optional environment file, execute the wrapper script once, and remain active after exit. State is systemd unit activation state and any CPU policy changes made by the wrapper. Dependencies are systemd, installed config file, installed libexec wrapper, and cpupower binary on PATH. Risks include path substitution errors, service reporting failed when one configured command fails, no automatic reapply after CPU hotplug, and container condition not covering all virtualized environments. Test signals are rendered unit inspection, `systemd-analyze verify`, and staged service execution with a temporary config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/cpupower.service.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/cpupower.sh -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/cpupower.sh

## Purpose
Shell wrapper executed by the cpupower systemd unit. It applies frequency settings, performance bias, and energy performance preference based on environment variables, accumulating a nonzero exit status if any command fails.

## Important APIs, Types, And Functions
Control flow prioritizes `FREQ` over governor/min/max settings, then separately applies `PERF_BIAS` and `EPP`. State changes are made through `cpupower frequency-set` and `cpupower set` commands. Dependencies are `/bin/sh`, cpupower in PATH, and environment loaded from `cpupower-service.conf`. Risks include word-splitting avoided for variable values but no validation before invoking cpupower, fixed command lookup through PATH, and partial success leaving some settings applied even when exit status is failure. Test signals are running with each variable combination, invalid values, and service exit code propagation.

## Control Flow
Control flow prioritizes `FREQ` over governor/min/max settings, then separately applies `PERF_BIAS` and `EPP`. State changes are made through `cpupower frequency-set` and `cpupower set` commands. Dependencies are `/bin/sh`, cpupower in PATH, and environment loaded from `cpupower-service.conf`. Risks include word-splitting avoided for variable values but no validation before invoking cpupower, fixed command lookup through PATH, and partial success leaving some settings applied even when exit status is failure. Test signals are running with each variable combination, invalid values, and service exit code propagation.

## State And Persistence
Control flow prioritizes `FREQ` over governor/min/max settings, then separately applies `PERF_BIAS` and `EPP`. State changes are made through `cpupower frequency-set` and `cpupower set` commands. Dependencies are `/bin/sh`, cpupower in PATH, and environment loaded from `cpupower-service.conf`. Risks include word-splitting avoided for variable values but no validation before invoking cpupower, fixed command lookup through PATH, and partial success leaving some settings applied even when exit status is failure. Test signals are running with each variable combination, invalid values, and service exit code propagation.

## Dependencies And Integration Points
Control flow prioritizes `FREQ` over governor/min/max settings, then separately applies `PERF_BIAS` and `EPP`. State changes are made through `cpupower frequency-set` and `cpupower set` commands. Dependencies are `/bin/sh`, cpupower in PATH, and environment loaded from `cpupower-service.conf`. Risks include word-splitting avoided for variable values but no validation before invoking cpupower, fixed command lookup through PATH, and partial success leaving some settings applied even when exit status is failure. Test signals are running with each variable combination, invalid values, and service exit code propagation.

## Risks And Edge Cases
Control flow prioritizes `FREQ` over governor/min/max settings, then separately applies `PERF_BIAS` and `EPP`. State changes are made through `cpupower frequency-set` and `cpupower set` commands. Dependencies are `/bin/sh`, cpupower in PATH, and environment loaded from `cpupower-service.conf`. Risks include word-splitting avoided for variable values but no validation before invoking cpupower, fixed command lookup through PATH, and partial success leaving some settings applied even when exit status is failure. Test signals are running with each variable combination, invalid values, and service exit code propagation.

## Test Signals
Control flow prioritizes `FREQ` over governor/min/max settings, then separately applies `PERF_BIAS` and `EPP`. State changes are made through `cpupower frequency-set` and `cpupower set` commands. Dependencies are `/bin/sh`, cpupower in PATH, and environment loaded from `cpupower-service.conf`. Risks include word-splitting avoided for variable values but no validation before invoking cpupower, fixed command lookup through PATH, and partial success leaving some settings applied even when exit status is failure. Test signals are running with each variable combination, invalid values, and service exit code propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/cpupower.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/Makefile

## Purpose
Builds legacy i386 cpupower debugging helpers: `centrino-decode`, `dump_psb`, `intel_gsic`, and `powernow-k8-decode`. It supports `O=` output, clean, and install into `bindir`.

## Important APIs, Types, And Functions
Control flow is direct one-command compile rules per utility; `intel_gsic` links `-llrmi`. State is produced helper binaries and installed copies. Dependencies are a C compiler, `/dev/mem`/MSR-capable runtime systems for tools, and liblrmi for `intel_gsic`. Risks include architecture-specific assumptions, no dependency tracking, liblrmi absence, and installing low-level debug tools by default if invoked. Test signals are builds with/without liblrmi, clean, staged install, and helper `--help`/error paths where available.

## Control Flow
Control flow is direct one-command compile rules per utility; `intel_gsic` links `-llrmi`. State is produced helper binaries and installed copies. Dependencies are a C compiler, `/dev/mem`/MSR-capable runtime systems for tools, and liblrmi for `intel_gsic`. Risks include architecture-specific assumptions, no dependency tracking, liblrmi absence, and installing low-level debug tools by default if invoked. Test signals are builds with/without liblrmi, clean, staged install, and helper `--help`/error paths where available.

## State And Persistence
Control flow is direct one-command compile rules per utility; `intel_gsic` links `-llrmi`. State is produced helper binaries and installed copies. Dependencies are a C compiler, `/dev/mem`/MSR-capable runtime systems for tools, and liblrmi for `intel_gsic`. Risks include architecture-specific assumptions, no dependency tracking, liblrmi absence, and installing low-level debug tools by default if invoked. Test signals are builds with/without liblrmi, clean, staged install, and helper `--help`/error paths where available.

## Dependencies And Integration Points
Control flow is direct one-command compile rules per utility; `intel_gsic` links `-llrmi`. State is produced helper binaries and installed copies. Dependencies are a C compiler, `/dev/mem`/MSR-capable runtime systems for tools, and liblrmi for `intel_gsic`. Risks include architecture-specific assumptions, no dependency tracking, liblrmi absence, and installing low-level debug tools by default if invoked. Test signals are builds with/without liblrmi, clean, staged install, and helper `--help`/error paths where available.

## Risks And Edge Cases
Control flow is direct one-command compile rules per utility; `intel_gsic` links `-llrmi`. State is produced helper binaries and installed copies. Dependencies are a C compiler, `/dev/mem`/MSR-capable runtime systems for tools, and liblrmi for `intel_gsic`. Risks include architecture-specific assumptions, no dependency tracking, liblrmi absence, and installing low-level debug tools by default if invoked. Test signals are builds with/without liblrmi, clean, staged install, and helper `--help`/error paths where available.

## Test Signals
Control flow is direct one-command compile rules per utility; `intel_gsic` links `-llrmi`. State is produced helper binaries and installed copies. Dependencies are a C compiler, `/dev/mem`/MSR-capable runtime systems for tools, and liblrmi for `intel_gsic`. Risks include architecture-specific assumptions, no dependency tracking, liblrmi absence, and installing low-level debug tools by default if invoked. Test signals are builds with/without liblrmi, clean, staged install, and helper `--help`/error paths where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/centrino-decode.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/centrino-decode.c

## Purpose
Debug helper for decoding Intel Enhanced SpeedStep Centrino performance status. It either reads `MSR_IA32_PERF_STATUS` from `/dev/cpu/N/msr` for a CPU or decodes a provided raw MSR value.

## Important APIs, Types, And Functions
Control flow parses the optional argument: values below `MCPU` are treated as CPU numbers, larger values as raw MSR content. `rdmsr()` opens the msr device, seeks to register 0x198, reads 8 bytes, and `decode()` prints multiplier and millivolts from low bits. State is read-only device access. Dependencies are msr kernel driver, root/read permissions, x86 hardware, and POSIX file APIs. Risks include `cpu > MCPU` allowing cpu 32 despite `MCPU=32`, ambiguous argument mode, old voltage formula applicability, and no detailed errno diagnostics. Test signals are raw decode values, missing msr device, non-root failure, and CPU argument boundaries.

## Control Flow
Control flow parses the optional argument: values below `MCPU` are treated as CPU numbers, larger values as raw MSR content. `rdmsr()` opens the msr device, seeks to register 0x198, reads 8 bytes, and `decode()` prints multiplier and millivolts from low bits. State is read-only device access. Dependencies are msr kernel driver, root/read permissions, x86 hardware, and POSIX file APIs. Risks include `cpu > MCPU` allowing cpu 32 despite `MCPU=32`, ambiguous argument mode, old voltage formula applicability, and no detailed errno diagnostics. Test signals are raw decode values, missing msr device, non-root failure, and CPU argument boundaries.

## State And Persistence
Control flow parses the optional argument: values below `MCPU` are treated as CPU numbers, larger values as raw MSR content. `rdmsr()` opens the msr device, seeks to register 0x198, reads 8 bytes, and `decode()` prints multiplier and millivolts from low bits. State is read-only device access. Dependencies are msr kernel driver, root/read permissions, x86 hardware, and POSIX file APIs. Risks include `cpu > MCPU` allowing cpu 32 despite `MCPU=32`, ambiguous argument mode, old voltage formula applicability, and no detailed errno diagnostics. Test signals are raw decode values, missing msr device, non-root failure, and CPU argument boundaries.

## Dependencies And Integration Points
Control flow parses the optional argument: values below `MCPU` are treated as CPU numbers, larger values as raw MSR content. `rdmsr()` opens the msr device, seeks to register 0x198, reads 8 bytes, and `decode()` prints multiplier and millivolts from low bits. State is read-only device access. Dependencies are msr kernel driver, root/read permissions, x86 hardware, and POSIX file APIs. Risks include `cpu > MCPU` allowing cpu 32 despite `MCPU=32`, ambiguous argument mode, old voltage formula applicability, and no detailed errno diagnostics. Test signals are raw decode values, missing msr device, non-root failure, and CPU argument boundaries.

## Risks And Edge Cases
Control flow parses the optional argument: values below `MCPU` are treated as CPU numbers, larger values as raw MSR content. `rdmsr()` opens the msr device, seeks to register 0x198, reads 8 bytes, and `decode()` prints multiplier and millivolts from low bits. State is read-only device access. Dependencies are msr kernel driver, root/read permissions, x86 hardware, and POSIX file APIs. Risks include `cpu > MCPU` allowing cpu 32 despite `MCPU=32`, ambiguous argument mode, old voltage formula applicability, and no detailed errno diagnostics. Test signals are raw decode values, missing msr device, non-root failure, and CPU argument boundaries.

## Test Signals
Control flow parses the optional argument: values below `MCPU` are treated as CPU numbers, larger values as raw MSR content. `rdmsr()` opens the msr device, seeks to register 0x198, reads 8 bytes, and `decode()` prints multiplier and millivolts from low bits. State is read-only device access. Dependencies are msr kernel driver, root/read permissions, x86 hardware, and POSIX file APIs. Risks include `cpu > MCPU` allowing cpu 32 despite `MCPU=32`, ambiguous argument mode, old voltage formula applicability, and no detailed errno diagnostics. Test signals are raw decode values, missing msr device, non-root failure, and CPU argument boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/centrino-decode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/dump_psb.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/dump_psb.c

## Purpose
Legacy AMD PowerNow! PSB scanner/decoder. It mmaps the BIOS memory region 0xc0000-0xfffff from `/dev/mem`, searches for `AMDK7PNOW!`, decodes PSB/PST packed structures, and prints frequencies/voltages from FID/VID tables.

## Important APIs, Types, And Functions
Control flow parses `-h`, `-r`, and `-n`, maps memory, scans every 16 bytes, and decodes matching PST records filtered by optional CPUID. State is read-only physical memory mapping. Dependencies are `/dev/mem`, root, x86 BIOS layout, packed struct assumptions, and getopt_long. Risks include no `MAP_FAILED` check before scanning, direct indexing into FID/VID tables without bounds checks, obsolete firmware formats, and low-memory access blocked by modern kernels. Test signals are help, permission failure, sample PSB blob decoding, invalid `-n/-r`, and running under kernels with strict devmem.

## Control Flow
Control flow parses `-h`, `-r`, and `-n`, maps memory, scans every 16 bytes, and decodes matching PST records filtered by optional CPUID. State is read-only physical memory mapping. Dependencies are `/dev/mem`, root, x86 BIOS layout, packed struct assumptions, and getopt_long. Risks include no `MAP_FAILED` check before scanning, direct indexing into FID/VID tables without bounds checks, obsolete firmware formats, and low-memory access blocked by modern kernels. Test signals are help, permission failure, sample PSB blob decoding, invalid `-n/-r`, and running under kernels with strict devmem.

## State And Persistence
Control flow parses `-h`, `-r`, and `-n`, maps memory, scans every 16 bytes, and decodes matching PST records filtered by optional CPUID. State is read-only physical memory mapping. Dependencies are `/dev/mem`, root, x86 BIOS layout, packed struct assumptions, and getopt_long. Risks include no `MAP_FAILED` check before scanning, direct indexing into FID/VID tables without bounds checks, obsolete firmware formats, and low-memory access blocked by modern kernels. Test signals are help, permission failure, sample PSB blob decoding, invalid `-n/-r`, and running under kernels with strict devmem.

## Dependencies And Integration Points
Control flow parses `-h`, `-r`, and `-n`, maps memory, scans every 16 bytes, and decodes matching PST records filtered by optional CPUID. State is read-only physical memory mapping. Dependencies are `/dev/mem`, root, x86 BIOS layout, packed struct assumptions, and getopt_long. Risks include no `MAP_FAILED` check before scanning, direct indexing into FID/VID tables without bounds checks, obsolete firmware formats, and low-memory access blocked by modern kernels. Test signals are help, permission failure, sample PSB blob decoding, invalid `-n/-r`, and running under kernels with strict devmem.

## Risks And Edge Cases
Control flow parses `-h`, `-r`, and `-n`, maps memory, scans every 16 bytes, and decodes matching PST records filtered by optional CPUID. State is read-only physical memory mapping. Dependencies are `/dev/mem`, root, x86 BIOS layout, packed struct assumptions, and getopt_long. Risks include no `MAP_FAILED` check before scanning, direct indexing into FID/VID tables without bounds checks, obsolete firmware formats, and low-memory access blocked by modern kernels. Test signals are help, permission failure, sample PSB blob decoding, invalid `-n/-r`, and running under kernels with strict devmem.

## Test Signals
Control flow parses `-h`, `-r`, and `-n`, maps memory, scans every 16 bytes, and decodes matching PST records filtered by optional CPUID. State is read-only physical memory mapping. Dependencies are `/dev/mem`, root, x86 BIOS layout, packed struct assumptions, and getopt_long. Risks include no `MAP_FAILED` check before scanning, direct indexing into FID/VID tables without bounds checks, obsolete firmware formats, and low-memory access blocked by modern kernels. Test signals are help, permission failure, sample PSB blob decoding, invalid `-n/-r`, and running under kernels with strict devmem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/dump_psb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/intel_gsic.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/intel_gsic.c

## Purpose
Debug helper that invokes the BIOS GSIC interface through vm86/real-mode interrupt 0x15 using liblrmi. It reports SpeedStep SMI command/event ports and flags or dumps registers if unsupported.

## Important APIs, Types, And Functions
Control flow initializes LRMI, sets EAX/EDX signature values, calls `LRMI_int(0x15)`, and formats returned registers with warnings for non-default SMI command/port values. State is BIOS interrupt side effects limited to the query. Dependencies are liblrmi, x86 real-mode BIOS availability, and sufficient privileges/environment to perform LRMI calls. Risks include not working on x86_64/UEFI-only systems, BIOS-specific behavior, and suggesting module parameters that can be risky if misused. Test signals are build/link with `-llrmi`, LRMI init failure, supported BIOS output, and unsupported-register dump.

## Control Flow
Control flow initializes LRMI, sets EAX/EDX signature values, calls `LRMI_int(0x15)`, and formats returned registers with warnings for non-default SMI command/port values. State is BIOS interrupt side effects limited to the query. Dependencies are liblrmi, x86 real-mode BIOS availability, and sufficient privileges/environment to perform LRMI calls. Risks include not working on x86_64/UEFI-only systems, BIOS-specific behavior, and suggesting module parameters that can be risky if misused. Test signals are build/link with `-llrmi`, LRMI init failure, supported BIOS output, and unsupported-register dump.

## State And Persistence
Control flow initializes LRMI, sets EAX/EDX signature values, calls `LRMI_int(0x15)`, and formats returned registers with warnings for non-default SMI command/port values. State is BIOS interrupt side effects limited to the query. Dependencies are liblrmi, x86 real-mode BIOS availability, and sufficient privileges/environment to perform LRMI calls. Risks include not working on x86_64/UEFI-only systems, BIOS-specific behavior, and suggesting module parameters that can be risky if misused. Test signals are build/link with `-llrmi`, LRMI init failure, supported BIOS output, and unsupported-register dump.

## Dependencies And Integration Points
Control flow initializes LRMI, sets EAX/EDX signature values, calls `LRMI_int(0x15)`, and formats returned registers with warnings for non-default SMI command/port values. State is BIOS interrupt side effects limited to the query. Dependencies are liblrmi, x86 real-mode BIOS availability, and sufficient privileges/environment to perform LRMI calls. Risks include not working on x86_64/UEFI-only systems, BIOS-specific behavior, and suggesting module parameters that can be risky if misused. Test signals are build/link with `-llrmi`, LRMI init failure, supported BIOS output, and unsupported-register dump.

## Risks And Edge Cases
Control flow initializes LRMI, sets EAX/EDX signature values, calls `LRMI_int(0x15)`, and formats returned registers with warnings for non-default SMI command/port values. State is BIOS interrupt side effects limited to the query. Dependencies are liblrmi, x86 real-mode BIOS availability, and sufficient privileges/environment to perform LRMI calls. Risks include not working on x86_64/UEFI-only systems, BIOS-specific behavior, and suggesting module parameters that can be risky if misused. Test signals are build/link with `-llrmi`, LRMI init failure, supported BIOS output, and unsupported-register dump.

## Test Signals
Control flow initializes LRMI, sets EAX/EDX signature values, calls `LRMI_int(0x15)`, and formats returned registers with warnings for non-default SMI command/port values. State is BIOS interrupt side effects limited to the query. Dependencies are liblrmi, x86 real-mode BIOS availability, and sufficient privileges/environment to perform LRMI calls. Risks include not working on x86_64/UEFI-only systems, BIOS-specific behavior, and suggesting module parameters that can be risky if misused. Test signals are build/link with `-llrmi`, LRMI init failure, supported BIOS output, and unsupported-register dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/intel_gsic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/powernow-k8-decode.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/powernow-k8-decode.c

## Purpose
Debug helper for AMD PowerNow-K8 current FID/VID status. It reads MSR 0xc0010042 from `/dev/cpu/N/msr`, extracts current FID/VID fields, and prints derived MHz and mV.

## Important APIs, Types, And Functions
Control flow parses optional CPU number, opens the msr device, seeks/reads 8 bytes, masks FID and VID, computes frequency as `800 + fid * 100` and voltage as `1550 - vid * 25`. State is read-only MSR access. Dependencies are msr driver, root/read permissions, PowerNow-K8-era AMD hardware, and POSIX file APIs. Risks include old formulas not matching newer CPUs, `cpu > MCPU` boundary, ignoring `lseek()` errors, and generic error messages. Test signals are missing msr device, raw known FID/VID cases via unit extraction, and running on supported hardware.

## Control Flow
Control flow parses optional CPU number, opens the msr device, seeks/reads 8 bytes, masks FID and VID, computes frequency as `800 + fid * 100` and voltage as `1550 - vid * 25`. State is read-only MSR access. Dependencies are msr driver, root/read permissions, PowerNow-K8-era AMD hardware, and POSIX file APIs. Risks include old formulas not matching newer CPUs, `cpu > MCPU` boundary, ignoring `lseek()` errors, and generic error messages. Test signals are missing msr device, raw known FID/VID cases via unit extraction, and running on supported hardware.

## State And Persistence
Control flow parses optional CPU number, opens the msr device, seeks/reads 8 bytes, masks FID and VID, computes frequency as `800 + fid * 100` and voltage as `1550 - vid * 25`. State is read-only MSR access. Dependencies are msr driver, root/read permissions, PowerNow-K8-era AMD hardware, and POSIX file APIs. Risks include old formulas not matching newer CPUs, `cpu > MCPU` boundary, ignoring `lseek()` errors, and generic error messages. Test signals are missing msr device, raw known FID/VID cases via unit extraction, and running on supported hardware.

## Dependencies And Integration Points
Control flow parses optional CPU number, opens the msr device, seeks/reads 8 bytes, masks FID and VID, computes frequency as `800 + fid * 100` and voltage as `1550 - vid * 25`. State is read-only MSR access. Dependencies are msr driver, root/read permissions, PowerNow-K8-era AMD hardware, and POSIX file APIs. Risks include old formulas not matching newer CPUs, `cpu > MCPU` boundary, ignoring `lseek()` errors, and generic error messages. Test signals are missing msr device, raw known FID/VID cases via unit extraction, and running on supported hardware.

## Risks And Edge Cases
Control flow parses optional CPU number, opens the msr device, seeks/reads 8 bytes, masks FID and VID, computes frequency as `800 + fid * 100` and voltage as `1550 - vid * 25`. State is read-only MSR access. Dependencies are msr driver, root/read permissions, PowerNow-K8-era AMD hardware, and POSIX file APIs. Risks include old formulas not matching newer CPUs, `cpu > MCPU` boundary, ignoring `lseek()` errors, and generic error messages. Test signals are missing msr device, raw known FID/VID cases via unit extraction, and running on supported hardware.

## Test Signals
Control flow parses optional CPU number, opens the msr device, seeks/reads 8 bytes, masks FID and VID, computes frequency as `800 + fid * 100` and voltage as `1550 - vid * 25`. State is read-only MSR access. Dependencies are msr driver, root/read permissions, PowerNow-K8-era AMD hardware, and POSIX file APIs. Risks include old formulas not matching newer CPUs, `cpu > MCPU` boundary, ignoring `lseek()` errors, and generic error messages. Test signals are missing msr device, raw known FID/VID cases via unit extraction, and running on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/powernow-k8-decode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/kernel/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/debug/kernel/Makefile

## Purpose
Kernel-module build file for the `cpufreq-test_tsc` debug module. It uses the running kernel build tree, optionally includes the module when `CONFIG_X86_TSC=y`, and installs modules under `/lib/modules/$(uname -r)/cpufrequtils/`.

## Important APIs, Types, And Functions
Control flow delegates to `$(MAKE) -C $(KDIR) M=$(CURDIR)`, cleans kernel build artifacts, and runs depmod after install. State is `.ko` and intermediate kernel module build files plus installed module files. Dependencies are kernel headers/build tree for the running kernel and the `CONFIG_X86_TSC` variable being supplied in the environment or make context. Risks include `obj-m` empty when config is not passed, installing under a nonstandard `cpufrequtils` directory, and building against the running kernel only. Test signals are `make CONFIG_X86_TSC=y`, clean, modinfo on the resulting module, and staged install review.

## Control Flow
Control flow delegates to `$(MAKE) -C $(KDIR) M=$(CURDIR)`, cleans kernel build artifacts, and runs depmod after install. State is `.ko` and intermediate kernel module build files plus installed module files. Dependencies are kernel headers/build tree for the running kernel and the `CONFIG_X86_TSC` variable being supplied in the environment or make context. Risks include `obj-m` empty when config is not passed, installing under a nonstandard `cpufrequtils` directory, and building against the running kernel only. Test signals are `make CONFIG_X86_TSC=y`, clean, modinfo on the resulting module, and staged install review.

## State And Persistence
Control flow delegates to `$(MAKE) -C $(KDIR) M=$(CURDIR)`, cleans kernel build artifacts, and runs depmod after install. State is `.ko` and intermediate kernel module build files plus installed module files. Dependencies are kernel headers/build tree for the running kernel and the `CONFIG_X86_TSC` variable being supplied in the environment or make context. Risks include `obj-m` empty when config is not passed, installing under a nonstandard `cpufrequtils` directory, and building against the running kernel only. Test signals are `make CONFIG_X86_TSC=y`, clean, modinfo on the resulting module, and staged install review.

## Dependencies And Integration Points
Control flow delegates to `$(MAKE) -C $(KDIR) M=$(CURDIR)`, cleans kernel build artifacts, and runs depmod after install. State is `.ko` and intermediate kernel module build files plus installed module files. Dependencies are kernel headers/build tree for the running kernel and the `CONFIG_X86_TSC` variable being supplied in the environment or make context. Risks include `obj-m` empty when config is not passed, installing under a nonstandard `cpufrequtils` directory, and building against the running kernel only. Test signals are `make CONFIG_X86_TSC=y`, clean, modinfo on the resulting module, and staged install review.

## Risks And Edge Cases
Control flow delegates to `$(MAKE) -C $(KDIR) M=$(CURDIR)`, cleans kernel build artifacts, and runs depmod after install. State is `.ko` and intermediate kernel module build files plus installed module files. Dependencies are kernel headers/build tree for the running kernel and the `CONFIG_X86_TSC` variable being supplied in the environment or make context. Risks include `obj-m` empty when config is not passed, installing under a nonstandard `cpufrequtils` directory, and building against the running kernel only. Test signals are `make CONFIG_X86_TSC=y`, clean, modinfo on the resulting module, and staged install review.

## Test Signals
Control flow delegates to `$(MAKE) -C $(KDIR) M=$(CURDIR)`, cleans kernel build artifacts, and runs depmod after install. State is `.ko` and intermediate kernel module build files plus installed module files. Dependencies are kernel headers/build tree for the running kernel and the `CONFIG_X86_TSC` variable being supplied in the environment or make context. Risks include `obj-m` empty when config is not passed, installing under a nonstandard `cpufrequtils` directory, and building against the running kernel only. Test signals are `make CONFIG_X86_TSC=y`, clean, modinfo on the resulting module, and staged install review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/kernel/cpufreq-test_tsc.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/debug/kernel/cpufreq-test_tsc.c

## Purpose
Debug kernel module intended to detect whether TSC-based delay timing remains stable across cpufreq transitions. Its init function reads the ACPI PM timer and TSC around repeated `mdelay(100)` intervals, logs deltas, then returns `-ENODEV` so loading fails after printing data.

## Important APIs, Types, And Functions
Control flow finds the PM timer I/O port from FADT fields, repeatedly reads a latched-safe PMTMR value and `rdtsc()`, logs `diff_pmtmr` and `diff_tsc`, and exits with failure by design. State is kernel log output only; it does not remain loaded. Dependencies are ACPI global FADT, x86 TSC, I/O port access, module infrastructure, and `mdelay()`. Risks include obsolete ACPI symbols on newer kernels, intentionally failing load confusing automation, direct I/O reads, and needing kernel build/root privileges. Test signals are dmesg output before/after a frequency transition, module build, and expected `modprobe` failure with logged measurements.

## Control Flow
Control flow finds the PM timer I/O port from FADT fields, repeatedly reads a latched-safe PMTMR value and `rdtsc()`, logs `diff_pmtmr` and `diff_tsc`, and exits with failure by design. State is kernel log output only; it does not remain loaded. Dependencies are ACPI global FADT, x86 TSC, I/O port access, module infrastructure, and `mdelay()`. Risks include obsolete ACPI symbols on newer kernels, intentionally failing load confusing automation, direct I/O reads, and needing kernel build/root privileges. Test signals are dmesg output before/after a frequency transition, module build, and expected `modprobe` failure with logged measurements.

## State And Persistence
Control flow finds the PM timer I/O port from FADT fields, repeatedly reads a latched-safe PMTMR value and `rdtsc()`, logs `diff_pmtmr` and `diff_tsc`, and exits with failure by design. State is kernel log output only; it does not remain loaded. Dependencies are ACPI global FADT, x86 TSC, I/O port access, module infrastructure, and `mdelay()`. Risks include obsolete ACPI symbols on newer kernels, intentionally failing load confusing automation, direct I/O reads, and needing kernel build/root privileges. Test signals are dmesg output before/after a frequency transition, module build, and expected `modprobe` failure with logged measurements.

## Dependencies And Integration Points
Control flow finds the PM timer I/O port from FADT fields, repeatedly reads a latched-safe PMTMR value and `rdtsc()`, logs `diff_pmtmr` and `diff_tsc`, and exits with failure by design. State is kernel log output only; it does not remain loaded. Dependencies are ACPI global FADT, x86 TSC, I/O port access, module infrastructure, and `mdelay()`. Risks include obsolete ACPI symbols on newer kernels, intentionally failing load confusing automation, direct I/O reads, and needing kernel build/root privileges. Test signals are dmesg output before/after a frequency transition, module build, and expected `modprobe` failure with logged measurements.

## Risks And Edge Cases
Control flow finds the PM timer I/O port from FADT fields, repeatedly reads a latched-safe PMTMR value and `rdtsc()`, logs `diff_pmtmr` and `diff_tsc`, and exits with failure by design. State is kernel log output only; it does not remain loaded. Dependencies are ACPI global FADT, x86 TSC, I/O port access, module infrastructure, and `mdelay()`. Risks include obsolete ACPI symbols on newer kernels, intentionally failing load confusing automation, direct I/O reads, and needing kernel build/root privileges. Test signals are dmesg output before/after a frequency transition, module build, and expected `modprobe` failure with logged measurements.

## Test Signals
Control flow finds the PM timer I/O port from FADT fields, repeatedly reads a latched-safe PMTMR value and `rdtsc()`, logs `diff_pmtmr` and `diff_tsc`, and exits with failure by design. State is kernel log output only; it does not remain loaded. Dependencies are ACPI global FADT, x86 TSC, I/O port access, module infrastructure, and `mdelay()`. Risks include obsolete ACPI symbols on newer kernels, intentionally failing load confusing automation, direct I/O reads, and needing kernel build/root privileges. Test signals are dmesg output before/after a frequency transition, module build, and expected `modprobe` failure with logged measurements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/kernel/cpufreq-test_tsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/x86_64/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/debug/x86_64/Makefile

## Purpose
Builds x86_64 variants of selected debug helpers by reusing the i386 source files for `centrino-decode` and `powernow-k8-decode`. It supports `O=`, clean, and install.

## Important APIs, Types, And Functions
Control flow is direct compile rules pointing at `../i386/*.c`; no `dump_psb` or `intel_gsic` targets are built for x86_64. State is produced helper binaries and installed copies. Dependencies are a C compiler, x86 MSR runtime support, and inherited source compatibility. Risks include duplicated build logic from i386, no dependency tracking, and legacy CPU assumptions on modern 64-bit systems. Test signals are build, clean, staged install, and helper behavior against missing/present `/dev/cpu/N/msr`.

## Control Flow
Control flow is direct compile rules pointing at `../i386/*.c`; no `dump_psb` or `intel_gsic` targets are built for x86_64. State is produced helper binaries and installed copies. Dependencies are a C compiler, x86 MSR runtime support, and inherited source compatibility. Risks include duplicated build logic from i386, no dependency tracking, and legacy CPU assumptions on modern 64-bit systems. Test signals are build, clean, staged install, and helper behavior against missing/present `/dev/cpu/N/msr`.

## State And Persistence
Control flow is direct compile rules pointing at `../i386/*.c`; no `dump_psb` or `intel_gsic` targets are built for x86_64. State is produced helper binaries and installed copies. Dependencies are a C compiler, x86 MSR runtime support, and inherited source compatibility. Risks include duplicated build logic from i386, no dependency tracking, and legacy CPU assumptions on modern 64-bit systems. Test signals are build, clean, staged install, and helper behavior against missing/present `/dev/cpu/N/msr`.

## Dependencies And Integration Points
Control flow is direct compile rules pointing at `../i386/*.c`; no `dump_psb` or `intel_gsic` targets are built for x86_64. State is produced helper binaries and installed copies. Dependencies are a C compiler, x86 MSR runtime support, and inherited source compatibility. Risks include duplicated build logic from i386, no dependency tracking, and legacy CPU assumptions on modern 64-bit systems. Test signals are build, clean, staged install, and helper behavior against missing/present `/dev/cpu/N/msr`.

## Risks And Edge Cases
Control flow is direct compile rules pointing at `../i386/*.c`; no `dump_psb` or `intel_gsic` targets are built for x86_64. State is produced helper binaries and installed copies. Dependencies are a C compiler, x86 MSR runtime support, and inherited source compatibility. Risks include duplicated build logic from i386, no dependency tracking, and legacy CPU assumptions on modern 64-bit systems. Test signals are build, clean, staged install, and helper behavior against missing/present `/dev/cpu/N/msr`.

## Test Signals
Control flow is direct compile rules pointing at `../i386/*.c`; no `dump_psb` or `intel_gsic` targets are built for x86_64. State is produced helper binaries and installed copies. Dependencies are a C compiler, x86 MSR runtime support, and inherited source compatibility. Risks include duplicated build logic from i386, no dependency tracking, and legacy CPU assumptions on modern 64-bit systems. Test signals are build, clean, staged install, and helper behavior against missing/present `/dev/cpu/N/msr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/x86_64/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/acpi_cppc.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/acpi_cppc.c

## Purpose
libcpupower helper for reading ACPI CPPC performance data from per-CPU sysfs. It maps enum values to files under `/sys/devices/system/cpu/cpuX/acpi_cppc/` and returns parsed unsigned values.

## Important APIs, Types, And Functions
`acpi_cppc_get_data()` validates the enum index, reads the file through `cpupower_read_sysfs()`, parses with `strtoull()`, and returns zero on failure. State is read-only sysfs access. Dependencies are `cpupower_intern.h`, `acpi_cppc.h`, kernel ACPI CPPC sysfs support, and libc parsing. Risks include zero being both a valid value and an error sentinel, not clearing `errno` before `strtoull()`, and returning `unsigned long` after parsing `unsigned long long`. Test signals are reads of each CPPC file on supported hardware, missing-file returns, malformed content, and 32-bit build truncation checks.

## Control Flow
`acpi_cppc_get_data()` validates the enum index, reads the file through `cpupower_read_sysfs()`, parses with `strtoull()`, and returns zero on failure. State is read-only sysfs access. Dependencies are `cpupower_intern.h`, `acpi_cppc.h`, kernel ACPI CPPC sysfs support, and libc parsing. Risks include zero being both a valid value and an error sentinel, not clearing `errno` before `strtoull()`, and returning `unsigned long` after parsing `unsigned long long`. Test signals are reads of each CPPC file on supported hardware, missing-file returns, malformed content, and 32-bit build truncation checks.

## State And Persistence
`acpi_cppc_get_data()` validates the enum index, reads the file through `cpupower_read_sysfs()`, parses with `strtoull()`, and returns zero on failure. State is read-only sysfs access. Dependencies are `cpupower_intern.h`, `acpi_cppc.h`, kernel ACPI CPPC sysfs support, and libc parsing. Risks include zero being both a valid value and an error sentinel, not clearing `errno` before `strtoull()`, and returning `unsigned long` after parsing `unsigned long long`. Test signals are reads of each CPPC file on supported hardware, missing-file returns, malformed content, and 32-bit build truncation checks.

## Dependencies And Integration Points
`acpi_cppc_get_data()` validates the enum index, reads the file through `cpupower_read_sysfs()`, parses with `strtoull()`, and returns zero on failure. State is read-only sysfs access. Dependencies are `cpupower_intern.h`, `acpi_cppc.h`, kernel ACPI CPPC sysfs support, and libc parsing. Risks include zero being both a valid value and an error sentinel, not clearing `errno` before `strtoull()`, and returning `unsigned long` after parsing `unsigned long long`. Test signals are reads of each CPPC file on supported hardware, missing-file returns, malformed content, and 32-bit build truncation checks.

## Risks And Edge Cases
`acpi_cppc_get_data()` validates the enum index, reads the file through `cpupower_read_sysfs()`, parses with `strtoull()`, and returns zero on failure. State is read-only sysfs access. Dependencies are `cpupower_intern.h`, `acpi_cppc.h`, kernel ACPI CPPC sysfs support, and libc parsing. Risks include zero being both a valid value and an error sentinel, not clearing `errno` before `strtoull()`, and returning `unsigned long` after parsing `unsigned long long`. Test signals are reads of each CPPC file on supported hardware, missing-file returns, malformed content, and 32-bit build truncation checks.

## Test Signals
`acpi_cppc_get_data()` validates the enum index, reads the file through `cpupower_read_sysfs()`, parses with `strtoull()`, and returns zero on failure. State is read-only sysfs access. Dependencies are `cpupower_intern.h`, `acpi_cppc.h`, kernel ACPI CPPC sysfs support, and libc parsing. Risks include zero being both a valid value and an error sentinel, not clearing `errno` before `strtoull()`, and returning `unsigned long` after parsing `unsigned long long`. Test signals are reads of each CPPC file on supported hardware, missing-file returns, malformed content, and 32-bit build truncation checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/acpi_cppc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/acpi_cppc.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/acpi_cppc.h

## Purpose
Public libcpupower header for ACPI CPPC values. It defines `enum acpi_cppc_value` entries such as highest/lowest/nominal performance, lowest/nominal frequency, reference performance, wraparound time, and declares `acpi_cppc_get_data()`.

## Important APIs, Types, And Functions
There is no runtime control flow; callers pass an enum and CPU number to retrieve sysfs data. Dependencies are the implementation in `acpi_cppc.c` and C consumers including this header. Risks include enum/file-order ABI coupling and the closing comment naming `_ACPI_CPPC_H` while the guard is `__ACPI_CPPC_H__`. Test signals are compile of C/C++ consumers and successful retrieval of each enum on CPPC systems.

## Control Flow
There is no runtime control flow; callers pass an enum and CPU number to retrieve sysfs data. Dependencies are the implementation in `acpi_cppc.c` and C consumers including this header. Risks include enum/file-order ABI coupling and the closing comment naming `_ACPI_CPPC_H` while the guard is `__ACPI_CPPC_H__`. Test signals are compile of C/C++ consumers and successful retrieval of each enum on CPPC systems.

## State And Persistence
There is no runtime control flow; callers pass an enum and CPU number to retrieve sysfs data. Dependencies are the implementation in `acpi_cppc.c` and C consumers including this header. Risks include enum/file-order ABI coupling and the closing comment naming `_ACPI_CPPC_H` while the guard is `__ACPI_CPPC_H__`. Test signals are compile of C/C++ consumers and successful retrieval of each enum on CPPC systems.

## Dependencies And Integration Points
There is no runtime control flow; callers pass an enum and CPU number to retrieve sysfs data. Dependencies are the implementation in `acpi_cppc.c` and C consumers including this header. Risks include enum/file-order ABI coupling and the closing comment naming `_ACPI_CPPC_H` while the guard is `__ACPI_CPPC_H__`. Test signals are compile of C/C++ consumers and successful retrieval of each enum on CPPC systems.

## Risks And Edge Cases
There is no runtime control flow; callers pass an enum and CPU number to retrieve sysfs data. Dependencies are the implementation in `acpi_cppc.c` and C consumers including this header. Risks include enum/file-order ABI coupling and the closing comment naming `_ACPI_CPPC_H` while the guard is `__ACPI_CPPC_H__`. Test signals are compile of C/C++ consumers and successful retrieval of each enum on CPPC systems.

## Test Signals
There is no runtime control flow; callers pass an enum and CPU number to retrieve sysfs data. Dependencies are the implementation in `acpi_cppc.c` and C consumers including this header. Risks include enum/file-order ABI coupling and the closing comment naming `_ACPI_CPPC_H` while the guard is `__ACPI_CPPC_H__`. Test signals are compile of C/C++ consumers and successful retrieval of each enum on CPPC systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/acpi_cppc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpufreq.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpufreq.c

## Purpose
Core libcpupower CPU frequency sysfs library. It reads current/hardware frequencies, limits, latency, driver/governor strings, available governors/frequencies/boost frequencies, affected/related CPU lists, stats, transitions, and writes policies/governors/specific frequencies.

## Important APIs, Types, And Functions
Control flow is organized around helpers that build `/sys/devices/system/cpu/cpuX/cpufreq/...` paths, read/write files, parse scalar/list values into allocated linked lists, and free via matching put functions. Policy writes validate governor names, choose min/max write order to avoid invalid intermediate ranges, then write the governor. State is heap-allocated result structs and kernel cpufreq sysfs changes on write APIs. Dependencies are cpufreq sysfs ABI, `cpupower_read_sysfs()`, POSIX file APIs, and `cpufreq.h` structs. Risks include zero-as-error ambiguity, missing `errno=0` before some `strtoul()` calls, allocation cleanup complexity, apparent source corruption in this snapshot (`return; return;`, duplicated `else`) that would break or alter behavior, no verification after writes, and requiring privileges for write APIs. Test signals are scalar reads across drivers, list parsing with trailing spaces/newlines, policy set min/max ordering, invalid governor rejection, stats parsing, and failure paths on systems without cpufreq.

## Control Flow
Control flow is organized around helpers that build `/sys/devices/system/cpu/cpuX/cpufreq/...` paths, read/write files, parse scalar/list values into allocated linked lists, and free via matching put functions. Policy writes validate governor names, choose min/max write order to avoid invalid intermediate ranges, then write the governor. State is heap-allocated result structs and kernel cpufreq sysfs changes on write APIs. Dependencies are cpufreq sysfs ABI, `cpupower_read_sysfs()`, POSIX file APIs, and `cpufreq.h` structs. Risks include zero-as-error ambiguity, missing `errno=0` before some `strtoul()` calls, allocation cleanup complexity, apparent source corruption in this snapshot (`return; return;`, duplicated `else`) that would break or alter behavior, no verification after writes, and requiring privileges for write APIs. Test signals are scalar reads across drivers, list parsing with trailing spaces/newlines, policy set min/max ordering, invalid governor rejection, stats parsing, and failure paths on systems without cpufreq.

## State And Persistence
Control flow is organized around helpers that build `/sys/devices/system/cpu/cpuX/cpufreq/...` paths, read/write files, parse scalar/list values into allocated linked lists, and free via matching put functions. Policy writes validate governor names, choose min/max write order to avoid invalid intermediate ranges, then write the governor. State is heap-allocated result structs and kernel cpufreq sysfs changes on write APIs. Dependencies are cpufreq sysfs ABI, `cpupower_read_sysfs()`, POSIX file APIs, and `cpufreq.h` structs. Risks include zero-as-error ambiguity, missing `errno=0` before some `strtoul()` calls, allocation cleanup complexity, apparent source corruption in this snapshot (`return; return;`, duplicated `else`) that would break or alter behavior, no verification after writes, and requiring privileges for write APIs. Test signals are scalar reads across drivers, list parsing with trailing spaces/newlines, policy set min/max ordering, invalid governor rejection, stats parsing, and failure paths on systems without cpufreq.

## Dependencies And Integration Points
Control flow is organized around helpers that build `/sys/devices/system/cpu/cpuX/cpufreq/...` paths, read/write files, parse scalar/list values into allocated linked lists, and free via matching put functions. Policy writes validate governor names, choose min/max write order to avoid invalid intermediate ranges, then write the governor. State is heap-allocated result structs and kernel cpufreq sysfs changes on write APIs. Dependencies are cpufreq sysfs ABI, `cpupower_read_sysfs()`, POSIX file APIs, and `cpufreq.h` structs. Risks include zero-as-error ambiguity, missing `errno=0` before some `strtoul()` calls, allocation cleanup complexity, apparent source corruption in this snapshot (`return; return;`, duplicated `else`) that would break or alter behavior, no verification after writes, and requiring privileges for write APIs. Test signals are scalar reads across drivers, list parsing with trailing spaces/newlines, policy set min/max ordering, invalid governor rejection, stats parsing, and failure paths on systems without cpufreq.

## Risks And Edge Cases
Control flow is organized around helpers that build `/sys/devices/system/cpu/cpuX/cpufreq/...` paths, read/write files, parse scalar/list values into allocated linked lists, and free via matching put functions. Policy writes validate governor names, choose min/max write order to avoid invalid intermediate ranges, then write the governor. State is heap-allocated result structs and kernel cpufreq sysfs changes on write APIs. Dependencies are cpufreq sysfs ABI, `cpupower_read_sysfs()`, POSIX file APIs, and `cpufreq.h` structs. Risks include zero-as-error ambiguity, missing `errno=0` before some `strtoul()` calls, allocation cleanup complexity, apparent source corruption in this snapshot (`return; return;`, duplicated `else`) that would break or alter behavior, no verification after writes, and requiring privileges for write APIs. Test signals are scalar reads across drivers, list parsing with trailing spaces/newlines, policy set min/max ordering, invalid governor rejection, stats parsing, and failure paths on systems without cpufreq.

## Test Signals
Control flow is organized around helpers that build `/sys/devices/system/cpu/cpuX/cpufreq/...` paths, read/write files, parse scalar/list values into allocated linked lists, and free via matching put functions. Policy writes validate governor names, choose min/max write order to avoid invalid intermediate ranges, then write the governor. State is heap-allocated result structs and kernel cpufreq sysfs changes on write APIs. Dependencies are cpufreq sysfs ABI, `cpupower_read_sysfs()`, POSIX file APIs, and `cpufreq.h` structs. Risks include zero-as-error ambiguity, missing `errno=0` before some `strtoul()` calls, allocation cleanup complexity, apparent source corruption in this snapshot (`return; return;`, duplicated `else`) that would break or alter behavior, no verification after writes, and requiring privileges for write APIs. Test signals are scalar reads across drivers, list parsing with trailing spaces/newlines, policy set min/max ordering, invalid governor rejection, stats parsing, and failure paths on systems without cpufreq.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpufreq.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpufreq.h

## Purpose
Public libcpupower CPU frequency API header. It defines policy/list/stat structs and declares read, free, policy modification, frequency setting, stats, and generic table-read functions.

## Important APIs, Types, And Functions
State ownership is explicit: many getters allocate linked lists or strings that must be released by corresponding `cpufreq_put_*` functions; write APIs mutate kernel cpufreq policy. Dependencies are C ABI consumers and `cpufreq.c`. Risks include linked-list nodes carrying a `first` backpointer that callers must not corrupt, zero/NULL return conventions requiring careful error handling, and API comments that may not cover all driver-specific sysfs absence cases. Test signals are ABI compile checks, leak tests for every getter/put pair, and write API behavior under unprivileged and privileged runs.

## Control Flow
State ownership is explicit: many getters allocate linked lists or strings that must be released by corresponding `cpufreq_put_*` functions; write APIs mutate kernel cpufreq policy. Dependencies are C ABI consumers and `cpufreq.c`. Risks include linked-list nodes carrying a `first` backpointer that callers must not corrupt, zero/NULL return conventions requiring careful error handling, and API comments that may not cover all driver-specific sysfs absence cases. Test signals are ABI compile checks, leak tests for every getter/put pair, and write API behavior under unprivileged and privileged runs.

## State And Persistence
State ownership is explicit: many getters allocate linked lists or strings that must be released by corresponding `cpufreq_put_*` functions; write APIs mutate kernel cpufreq policy. Dependencies are C ABI consumers and `cpufreq.c`. Risks include linked-list nodes carrying a `first` backpointer that callers must not corrupt, zero/NULL return conventions requiring careful error handling, and API comments that may not cover all driver-specific sysfs absence cases. Test signals are ABI compile checks, leak tests for every getter/put pair, and write API behavior under unprivileged and privileged runs.

## Dependencies And Integration Points
State ownership is explicit: many getters allocate linked lists or strings that must be released by corresponding `cpufreq_put_*` functions; write APIs mutate kernel cpufreq policy. Dependencies are C ABI consumers and `cpufreq.c`. Risks include linked-list nodes carrying a `first` backpointer that callers must not corrupt, zero/NULL return conventions requiring careful error handling, and API comments that may not cover all driver-specific sysfs absence cases. Test signals are ABI compile checks, leak tests for every getter/put pair, and write API behavior under unprivileged and privileged runs.

## Risks And Edge Cases
State ownership is explicit: many getters allocate linked lists or strings that must be released by corresponding `cpufreq_put_*` functions; write APIs mutate kernel cpufreq policy. Dependencies are C ABI consumers and `cpufreq.c`. Risks include linked-list nodes carrying a `first` backpointer that callers must not corrupt, zero/NULL return conventions requiring careful error handling, and API comments that may not cover all driver-specific sysfs absence cases. Test signals are ABI compile checks, leak tests for every getter/put pair, and write API behavior under unprivileged and privileged runs.

## Test Signals
State ownership is explicit: many getters allocate linked lists or strings that must be released by corresponding `cpufreq_put_*` functions; write APIs mutate kernel cpufreq policy. Dependencies are C ABI consumers and `cpufreq.c`. Risks include linked-list nodes carrying a `first` backpointer that callers must not corrupt, zero/NULL return conventions requiring careful error handling, and API comments that may not cover all driver-specific sysfs absence cases. Test signals are ABI compile checks, leak tests for every getter/put pair, and write API behavior under unprivileged and privileged runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpufreq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpuidle.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpuidle.c

## Purpose
libcpupower CPU idle sysfs library. It reads per-state idle metrics and strings, checks/enables/disables idle states, counts idle states, and reads global cpuidle governor/driver names.

## Important APIs, Types, And Functions
Control flow builds `/sys/devices/system/cpu/cpuX/cpuidle/stateY/...` paths for per-state operations and `/sys/devices/system/cpu/cpuidle/...` for global strings. It uses `stat()` to detect feature support, `read()`/`write()` for state files, parses numeric values with `strtoull()`, and allocates strings with `strdup()`. State is read-only for getters and kernel sysfs mutation for disable/enable. Dependencies are cpuidle sysfs ABI, `cpupower_read_sysfs()`, and `cpuidle.h`. Risks include state count loop incrementing path names in a non-obvious way, zero-as-error ambiguity, write permission errors collapsed to `-3`, and getters returning allocated strings without corresponding public free helper other than plain `free()`. Test signals are systems with no cpuidle, disabled-state support absent/present, permission failures, count accuracy, and string trim behavior.

## Control Flow
Control flow builds `/sys/devices/system/cpu/cpuX/cpuidle/stateY/...` paths for per-state operations and `/sys/devices/system/cpu/cpuidle/...` for global strings. It uses `stat()` to detect feature support, `read()`/`write()` for state files, parses numeric values with `strtoull()`, and allocates strings with `strdup()`. State is read-only for getters and kernel sysfs mutation for disable/enable. Dependencies are cpuidle sysfs ABI, `cpupower_read_sysfs()`, and `cpuidle.h`. Risks include state count loop incrementing path names in a non-obvious way, zero-as-error ambiguity, write permission errors collapsed to `-3`, and getters returning allocated strings without corresponding public free helper other than plain `free()`. Test signals are systems with no cpuidle, disabled-state support absent/present, permission failures, count accuracy, and string trim behavior.

## State And Persistence
Control flow builds `/sys/devices/system/cpu/cpuX/cpuidle/stateY/...` paths for per-state operations and `/sys/devices/system/cpu/cpuidle/...` for global strings. It uses `stat()` to detect feature support, `read()`/`write()` for state files, parses numeric values with `strtoull()`, and allocates strings with `strdup()`. State is read-only for getters and kernel sysfs mutation for disable/enable. Dependencies are cpuidle sysfs ABI, `cpupower_read_sysfs()`, and `cpuidle.h`. Risks include state count loop incrementing path names in a non-obvious way, zero-as-error ambiguity, write permission errors collapsed to `-3`, and getters returning allocated strings without corresponding public free helper other than plain `free()`. Test signals are systems with no cpuidle, disabled-state support absent/present, permission failures, count accuracy, and string trim behavior.

## Dependencies And Integration Points
Control flow builds `/sys/devices/system/cpu/cpuX/cpuidle/stateY/...` paths for per-state operations and `/sys/devices/system/cpu/cpuidle/...` for global strings. It uses `stat()` to detect feature support, `read()`/`write()` for state files, parses numeric values with `strtoull()`, and allocates strings with `strdup()`. State is read-only for getters and kernel sysfs mutation for disable/enable. Dependencies are cpuidle sysfs ABI, `cpupower_read_sysfs()`, and `cpuidle.h`. Risks include state count loop incrementing path names in a non-obvious way, zero-as-error ambiguity, write permission errors collapsed to `-3`, and getters returning allocated strings without corresponding public free helper other than plain `free()`. Test signals are systems with no cpuidle, disabled-state support absent/present, permission failures, count accuracy, and string trim behavior.

## Risks And Edge Cases
Control flow builds `/sys/devices/system/cpu/cpuX/cpuidle/stateY/...` paths for per-state operations and `/sys/devices/system/cpu/cpuidle/...` for global strings. It uses `stat()` to detect feature support, `read()`/`write()` for state files, parses numeric values with `strtoull()`, and allocates strings with `strdup()`. State is read-only for getters and kernel sysfs mutation for disable/enable. Dependencies are cpuidle sysfs ABI, `cpupower_read_sysfs()`, and `cpuidle.h`. Risks include state count loop incrementing path names in a non-obvious way, zero-as-error ambiguity, write permission errors collapsed to `-3`, and getters returning allocated strings without corresponding public free helper other than plain `free()`. Test signals are systems with no cpuidle, disabled-state support absent/present, permission failures, count accuracy, and string trim behavior.

## Test Signals
Control flow builds `/sys/devices/system/cpu/cpuX/cpuidle/stateY/...` paths for per-state operations and `/sys/devices/system/cpu/cpuidle/...` for global strings. It uses `stat()` to detect feature support, `read()`/`write()` for state files, parses numeric values with `strtoull()`, and allocates strings with `strdup()`. State is read-only for getters and kernel sysfs mutation for disable/enable. Dependencies are cpuidle sysfs ABI, `cpupower_read_sysfs()`, and `cpuidle.h`. Risks include state count loop incrementing path names in a non-obvious way, zero-as-error ambiguity, write permission errors collapsed to `-3`, and getters returning allocated strings without corresponding public free helper other than plain `free()`. Test signals are systems with no cpuidle, disabled-state support absent/present, permission failures, count accuracy, and string trim behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpuidle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpuidle.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpuidle.h

## Purpose
Public header for libcpupower CPU idle APIs. It declares functions to query and set idle-state disabled status, read latency/residency/usage/time/name/description, count states, and get global governor/driver.

## Important APIs, Types, And Functions
There is no control flow in the header; callers own returned strings and must understand negative return conventions for disable APIs. Dependencies are `cpuidle.c` and sysfs availability at runtime. Risks include no explicit free helper for returned strings, unsigned state count returning zero for unsupported/error cases, and guard closing comment naming a different header. Test signals are C/C++ compile checks, SWIG binding generation, and Python binding smoke tests.

## Control Flow
There is no control flow in the header; callers own returned strings and must understand negative return conventions for disable APIs. Dependencies are `cpuidle.c` and sysfs availability at runtime. Risks include no explicit free helper for returned strings, unsigned state count returning zero for unsupported/error cases, and guard closing comment naming a different header. Test signals are C/C++ compile checks, SWIG binding generation, and Python binding smoke tests.

## State And Persistence
There is no control flow in the header; callers own returned strings and must understand negative return conventions for disable APIs. Dependencies are `cpuidle.c` and sysfs availability at runtime. Risks include no explicit free helper for returned strings, unsigned state count returning zero for unsupported/error cases, and guard closing comment naming a different header. Test signals are C/C++ compile checks, SWIG binding generation, and Python binding smoke tests.

## Dependencies And Integration Points
There is no control flow in the header; callers own returned strings and must understand negative return conventions for disable APIs. Dependencies are `cpuidle.c` and sysfs availability at runtime. Risks include no explicit free helper for returned strings, unsigned state count returning zero for unsupported/error cases, and guard closing comment naming a different header. Test signals are C/C++ compile checks, SWIG binding generation, and Python binding smoke tests.

## Risks And Edge Cases
There is no control flow in the header; callers own returned strings and must understand negative return conventions for disable APIs. Dependencies are `cpuidle.c` and sysfs availability at runtime. Risks include no explicit free helper for returned strings, unsigned state count returning zero for unsupported/error cases, and guard closing comment naming a different header. Test signals are C/C++ compile checks, SWIG binding generation, and Python binding smoke tests.

## Test Signals
There is no control flow in the header; callers own returned strings and must understand negative return conventions for disable APIs. Dependencies are `cpuidle.c` and sysfs availability at runtime. Risks include no explicit free helper for returned strings, unsigned state count returning zero for unsupported/error cases, and guard closing comment naming a different header. Test signals are C/C++ compile checks, SWIG binding generation, and Python binding smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpuidle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpupower.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpupower.c

## Purpose
Common libcpupower sysfs and topology helpers. It validates paths, reads/writes sysfs files, checks CPU online status, and builds a sorted CPU topology summary with package/core/CPU IDs and core sibling lists.

## Important APIs, Types, And Functions
Control flow for sysfs helpers is open/read/write/close with NUL termination for reads. `cpupower_is_cpu_online()` treats missing `online` as online for non-hotplug kernels. `get_cpu_topology()` allocates `core_info` for configured CPUs, reads topology files, sorts by core CPU list to count physical cores, then sorts by package/core/cpu to count packages. State is heap topology data released by `cpu_topology_release()` and kernel sysfs writes via `cpupower_write_sysfs()`. Dependencies are sysfs CPU topology ABI, `sysconf(_SC_NPROCESSORS_CONF)`, qsort, and `cpupower.h`. Risks include `CPULIST_BUFFER` being only 5 bytes for larger CPU lists, `cpupower_write_sysfs()` writing `buflen - 1` bytes, package count edge cases when first entries are invalid, and no threads-per-core calculation despite struct field. Test signals are topology on single/multi-socket/SMT/offline-CPU systems, large CPU numbers, write helper byte-count tests, and memory leak checks.

## Control Flow
Control flow for sysfs helpers is open/read/write/close with NUL termination for reads. `cpupower_is_cpu_online()` treats missing `online` as online for non-hotplug kernels. `get_cpu_topology()` allocates `core_info` for configured CPUs, reads topology files, sorts by core CPU list to count physical cores, then sorts by package/core/cpu to count packages. State is heap topology data released by `cpu_topology_release()` and kernel sysfs writes via `cpupower_write_sysfs()`. Dependencies are sysfs CPU topology ABI, `sysconf(_SC_NPROCESSORS_CONF)`, qsort, and `cpupower.h`. Risks include `CPULIST_BUFFER` being only 5 bytes for larger CPU lists, `cpupower_write_sysfs()` writing `buflen - 1` bytes, package count edge cases when first entries are invalid, and no threads-per-core calculation despite struct field. Test signals are topology on single/multi-socket/SMT/offline-CPU systems, large CPU numbers, write helper byte-count tests, and memory leak checks.

## State And Persistence
Control flow for sysfs helpers is open/read/write/close with NUL termination for reads. `cpupower_is_cpu_online()` treats missing `online` as online for non-hotplug kernels. `get_cpu_topology()` allocates `core_info` for configured CPUs, reads topology files, sorts by core CPU list to count physical cores, then sorts by package/core/cpu to count packages. State is heap topology data released by `cpu_topology_release()` and kernel sysfs writes via `cpupower_write_sysfs()`. Dependencies are sysfs CPU topology ABI, `sysconf(_SC_NPROCESSORS_CONF)`, qsort, and `cpupower.h`. Risks include `CPULIST_BUFFER` being only 5 bytes for larger CPU lists, `cpupower_write_sysfs()` writing `buflen - 1` bytes, package count edge cases when first entries are invalid, and no threads-per-core calculation despite struct field. Test signals are topology on single/multi-socket/SMT/offline-CPU systems, large CPU numbers, write helper byte-count tests, and memory leak checks.

## Dependencies And Integration Points
Control flow for sysfs helpers is open/read/write/close with NUL termination for reads. `cpupower_is_cpu_online()` treats missing `online` as online for non-hotplug kernels. `get_cpu_topology()` allocates `core_info` for configured CPUs, reads topology files, sorts by core CPU list to count physical cores, then sorts by package/core/cpu to count packages. State is heap topology data released by `cpu_topology_release()` and kernel sysfs writes via `cpupower_write_sysfs()`. Dependencies are sysfs CPU topology ABI, `sysconf(_SC_NPROCESSORS_CONF)`, qsort, and `cpupower.h`. Risks include `CPULIST_BUFFER` being only 5 bytes for larger CPU lists, `cpupower_write_sysfs()` writing `buflen - 1` bytes, package count edge cases when first entries are invalid, and no threads-per-core calculation despite struct field. Test signals are topology on single/multi-socket/SMT/offline-CPU systems, large CPU numbers, write helper byte-count tests, and memory leak checks.

## Risks And Edge Cases
Control flow for sysfs helpers is open/read/write/close with NUL termination for reads. `cpupower_is_cpu_online()` treats missing `online` as online for non-hotplug kernels. `get_cpu_topology()` allocates `core_info` for configured CPUs, reads topology files, sorts by core CPU list to count physical cores, then sorts by package/core/cpu to count packages. State is heap topology data released by `cpu_topology_release()` and kernel sysfs writes via `cpupower_write_sysfs()`. Dependencies are sysfs CPU topology ABI, `sysconf(_SC_NPROCESSORS_CONF)`, qsort, and `cpupower.h`. Risks include `CPULIST_BUFFER` being only 5 bytes for larger CPU lists, `cpupower_write_sysfs()` writing `buflen - 1` bytes, package count edge cases when first entries are invalid, and no threads-per-core calculation despite struct field. Test signals are topology on single/multi-socket/SMT/offline-CPU systems, large CPU numbers, write helper byte-count tests, and memory leak checks.

## Test Signals
Control flow for sysfs helpers is open/read/write/close with NUL termination for reads. `cpupower_is_cpu_online()` treats missing `online` as online for non-hotplug kernels. `get_cpu_topology()` allocates `core_info` for configured CPUs, reads topology files, sorts by core CPU list to count physical cores, then sorts by package/core/cpu to count packages. State is heap topology data released by `cpu_topology_release()` and kernel sysfs writes via `cpupower_write_sysfs()`. Dependencies are sysfs CPU topology ABI, `sysconf(_SC_NPROCESSORS_CONF)`, qsort, and `cpupower.h`. Risks include `CPULIST_BUFFER` being only 5 bytes for larger CPU lists, `cpupower_write_sysfs()` writing `buflen - 1` bytes, package count edge cases when first entries are invalid, and no threads-per-core calculation despite struct field. Test signals are topology on single/multi-socket/SMT/offline-CPU systems, large CPU numbers, write helper byte-count tests, and memory leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpupower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpupower.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpupower.h

## Purpose
Public common libcpupower header. It defines `struct cpupower_topology`, `struct cpuid_core_info`, `CPULIST_BUFFER`, and declares topology retrieval/release plus CPU online checking.

## Important APIs, Types, And Functions
State ownership is through `get_cpu_topology()`, which allocates `core_info` and requires `cpu_topology_release()`. Dependencies are `cpupower.c` and CPU topology sysfs at runtime. Risks include small `CPULIST_BUFFER`, `threads` field not populated by the current implementation, bitfield representation for `is_online`, and callers needing to handle negative returns. Test signals are ABI compile checks and topology release/leak tests.

## Control Flow
State ownership is through `get_cpu_topology()`, which allocates `core_info` and requires `cpu_topology_release()`. Dependencies are `cpupower.c` and CPU topology sysfs at runtime. Risks include small `CPULIST_BUFFER`, `threads` field not populated by the current implementation, bitfield representation for `is_online`, and callers needing to handle negative returns. Test signals are ABI compile checks and topology release/leak tests.

## State And Persistence
State ownership is through `get_cpu_topology()`, which allocates `core_info` and requires `cpu_topology_release()`. Dependencies are `cpupower.c` and CPU topology sysfs at runtime. Risks include small `CPULIST_BUFFER`, `threads` field not populated by the current implementation, bitfield representation for `is_online`, and callers needing to handle negative returns. Test signals are ABI compile checks and topology release/leak tests.

## Dependencies And Integration Points
State ownership is through `get_cpu_topology()`, which allocates `core_info` and requires `cpu_topology_release()`. Dependencies are `cpupower.c` and CPU topology sysfs at runtime. Risks include small `CPULIST_BUFFER`, `threads` field not populated by the current implementation, bitfield representation for `is_online`, and callers needing to handle negative returns. Test signals are ABI compile checks and topology release/leak tests.

## Risks And Edge Cases
State ownership is through `get_cpu_topology()`, which allocates `core_info` and requires `cpu_topology_release()`. Dependencies are `cpupower.c` and CPU topology sysfs at runtime. Risks include small `CPULIST_BUFFER`, `threads` field not populated by the current implementation, bitfield representation for `is_online`, and callers needing to handle negative returns. Test signals are ABI compile checks and topology release/leak tests.

## Test Signals
State ownership is through `get_cpu_topology()`, which allocates `core_info` and requires `cpu_topology_release()`. Dependencies are `cpupower.c` and CPU topology sysfs at runtime. Risks include small `CPULIST_BUFFER`, `threads` field not populated by the current implementation, bitfield representation for `is_online`, and callers needing to handle negative returns. Test signals are ABI compile checks and topology release/leak tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpupower.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpupower_intern.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpupower_intern.h

## Purpose
Internal libcpupower constants and helper prototypes. It defines the sysfs CPU root path, maximum line/path lengths, and declarations for path validation plus generic sysfs read/write helpers.

## Important APIs, Types, And Functions
There is no runtime control flow in this header; it standardizes path and buffer sizes used by cpufreq, cpuidle, CPPC, and topology code. State is compile-time only. Dependencies are implementations in `cpupower.c`. Risks include fixed `SYSFS_PATH_MAX=255` truncating long sysfs paths and shared helper prototypes exposing internal functions to any source that includes the header. Test signals are compiler warnings for path truncation and unit tests of helpers against temporary sysfs-like files.

## Control Flow
There is no runtime control flow in this header; it standardizes path and buffer sizes used by cpufreq, cpuidle, CPPC, and topology code. State is compile-time only. Dependencies are implementations in `cpupower.c`. Risks include fixed `SYSFS_PATH_MAX=255` truncating long sysfs paths and shared helper prototypes exposing internal functions to any source that includes the header. Test signals are compiler warnings for path truncation and unit tests of helpers against temporary sysfs-like files.

## State And Persistence
There is no runtime control flow in this header; it standardizes path and buffer sizes used by cpufreq, cpuidle, CPPC, and topology code. State is compile-time only. Dependencies are implementations in `cpupower.c`. Risks include fixed `SYSFS_PATH_MAX=255` truncating long sysfs paths and shared helper prototypes exposing internal functions to any source that includes the header. Test signals are compiler warnings for path truncation and unit tests of helpers against temporary sysfs-like files.

## Dependencies And Integration Points
There is no runtime control flow in this header; it standardizes path and buffer sizes used by cpufreq, cpuidle, CPPC, and topology code. State is compile-time only. Dependencies are implementations in `cpupower.c`. Risks include fixed `SYSFS_PATH_MAX=255` truncating long sysfs paths and shared helper prototypes exposing internal functions to any source that includes the header. Test signals are compiler warnings for path truncation and unit tests of helpers against temporary sysfs-like files.

## Risks And Edge Cases
There is no runtime control flow in this header; it standardizes path and buffer sizes used by cpufreq, cpuidle, CPPC, and topology code. State is compile-time only. Dependencies are implementations in `cpupower.c`. Risks include fixed `SYSFS_PATH_MAX=255` truncating long sysfs paths and shared helper prototypes exposing internal functions to any source that includes the header. Test signals are compiler warnings for path truncation and unit tests of helpers against temporary sysfs-like files.

## Test Signals
There is no runtime control flow in this header; it standardizes path and buffer sizes used by cpufreq, cpuidle, CPPC, and topology code. State is compile-time only. Dependencies are implementations in `cpupower.c`. Risks include fixed `SYSFS_PATH_MAX=255` truncating long sysfs paths and shared helper prototypes exposing internal functions to any source that includes the header. Test signals are compiler warnings for path truncation and unit tests of helpers against temporary sysfs-like files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpupower_intern.h -->
