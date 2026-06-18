# sources/distributed-fs/ceph-client/tools/perf/util/vdso.c

## Purpose

`vdso.c` materializes the process vDSO image as temporary files and registers matching DSOs in a machine. This lets perf symbolize vDSO samples, including compat 32-bit and x32 vDSOs on 64-bit builds when helper programs are available.

## Important APIs, Types, and Functions

Internal `struct vdso_file` tracks whether a temp file was found or errored, the temp filename template, DSO name, and optional helper program. `struct vdso_info` contains native and compat vDSO slots. Public functions are `machine__exit_vdso()`, `machine__findnew_vdso()`, and `dso__is_vdso()`. Internal helpers copy the in-memory native vDSO via `find_map()`, create DSOs, determine a thread's DSO type from maps, run compat helper programs, and find existing vDSO DSOs.

## Control Flow and State

`machine__findnew_vdso()` lazily allocates `machine->vdso_info`, checks for an existing type-appropriate vDSO DSO, tries compat vDSO creation for 32-bit/x32 threads on 64-bit hosts, otherwise copies the current process `[vdso]` mapping to `/tmp/perf-vdso.so-XXXXXX` and adds a DSO with that long name. `machine__exit_vdso()` unlinks any created temp files and frees the info. `dso__is_vdso()` checks short names against native and compat constants.

## Dependencies and Integration Points

It depends on DSOs, maps, symbols, machine, thread maps, temporary-file APIs, helper binaries `perf-read-vdso32` and `perf-read-vdsox32`, and `find-map.c`. It integrates with symbol resolution for user samples in vDSO regions.

## State and Persistence Behavior

Temporary files persist until `machine__exit_vdso()` unlinks them. `vdso_file` caches success or failure to avoid repeated work. The DSO list stores references to the temp file paths.

## Risks and Test Signals

Risks include temp-file leaks, helper program failures, wrong DSO type selection for mixed 32/64-bit workloads, copying the current process vDSO when analyzing a different environment, and stale error caching. Tests should symbolize native vDSO samples, exercise compat helper availability and absence, verify cleanup unlinks temp files, detect `dso__is_vdso()` names, and analyze workloads with mixed bitness.
