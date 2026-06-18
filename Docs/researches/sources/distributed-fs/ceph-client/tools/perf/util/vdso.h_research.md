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
