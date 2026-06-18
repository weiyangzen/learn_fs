<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pe-file-parsing.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/pe-file-parsing.c

## Purpose

This selftest validates perf's PE/COFF support when libbfd is enabled: reading a PE build-id, resolving a GNU debuglink, loading external debug symbols, and finding `main` in a Windows binary fixture.

## Research

The main helper is `run_dir`, which builds paths for `pe-file.exe` and `pe-file.exe.debug`, calls `filename__read_build_id`, checks the fixed 16-byte CodeView build id, verifies `filename__read_debuglink`, creates a `dso`, loads BFD symbols with `dso__load_bfd_symbols`, sorts by name, and uses `dso__find_symbol_by_name`. `test__pe_file_parsing` searches `./tests` first, then the installed perf tests directory from `get_argv_exec_path`. If `HAVE_LIBBFD_SUPPORT` is absent, the suite skips. State is limited to local buffers and a temporary DSO object. Dependencies include libbfd, `util/build-id.h`, `util/symbol.h`, and `util/dso.h`. Risks are fixture drift, missing installed test data, platform builds without libbfd, and build-id byte-order mistakes. Strong test signals are exact build-id equality, debuglink name equality, successful BFD symbol loading, and finding `main`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pe-file-parsing.c -->
