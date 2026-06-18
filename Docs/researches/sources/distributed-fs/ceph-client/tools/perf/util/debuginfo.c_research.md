# sources/distributed-fs/ceph-client/tools/perf/util/debuginfo.c

## Purpose

`debuginfo.c` wraps elfutils DWARF/DWFL access for perf. It opens distro or build-id debuginfo files, falls back to the original binary under symfs, exposes text-section offset lookup, and optionally retrieves source files from debuginfod.

## Important APIs, Types, and Functions

`debuginfo__new()` is the public constructor. It uses `dso__read_binary_type_filename()` across Fedora, Ubuntu, OpenEmbedded, build-id, and mixed-up Ubuntu debuginfo locations before falling back to the given path. `__debuginfo__new()` and `debuginfo__init_offline_dwarf()` allocate and initialize DWFL/DWARF state. `debuginfo__delete()` releases it. `debuginfo__get_text_offset()` finds relocation `.text` section offsets. `get_source_from_debuginfod()` wraps `debuginfod_find_source()` when enabled.

## Control Flow

The constructor creates a temporary DSO for the path, reads its build ID if available, tries known debuginfo binary types in order, releases the DSO, and opens the symfs-joined original binary if no separate debuginfo succeeds. DWFL initialization reports an offline module, obtains DWARF and build-id data, then finalizes reporting. Text offset lookup scans DWFL relocation entries for `.text` and reads its ELF section header.

## State and Persistence Behavior

Runtime state is `struct debuginfo` with DWARF handle, DWFL module/session, relocation bias, and build ID pointer. `debuginfo_path` is a static callback variable for standard debuginfo lookup. Debuginfod may create local cache entries through elfutils behavior, but this file only receives and returns a fetched path.

## Dependencies and Integration Points

It depends on elfutils DWARF/DWFL/GELF APIs, perf DSO/build-id/symbol helpers, symfs path joining, debug logging, and optional debuginfod. It supports source-line, probe, annotation, and symbol consumers that need DWARF data.

## Risks and Edge Cases

Open failures collapse to `-ENOENT`, losing some detailed diagnostics. The FD passed to `dwfl_report_offline()` is owned by DWFL on success but must be closed on early failure when DWFL was not created. `debuginfo__get_text_offset()` returns success even if `.text` was not found after scanning, so callers need to validate output initialization. Debuginfod build ID length is passed as zero, relying on elfutils interpretation of the string argument.

## Test Signals

Tests should cover separate distro debuginfo discovery, build-id lookup, fallback binary opening, invalid ELF files, symfs paths, kernel module `.text` offset with and without adjustment, debuginfod success/failure, and builds without debuginfod support.
