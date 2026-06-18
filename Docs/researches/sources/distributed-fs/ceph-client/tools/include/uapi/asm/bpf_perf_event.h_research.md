# sources/distributed-fs/ceph-client/tools/include/uapi/asm/bpf_perf_event.h

## Purpose
Routes BPF perf-event UAPI includes to architecture-specific register-context definitions when available, otherwise to the generic fallback.

## Important APIs, Types, and Functions
Branches on `__aarch64__`, `__arc__`, `__s390__`, `__riscv`, and `__loongarch__`, including the corresponding `arch/*/include/uapi/asm/bpf_perf_event.h`; otherwise includes `<uapi/asm-generic/bpf_perf_event.h>`.

## Control Flow, State, and Persistence
Preprocessor include selection only. No runtime behavior or persistent state exists.

## Dependencies and Integration
Depends on compiler target macros and relative arch header paths. It integrates with BPF/perf sample code that needs the correct `bpf_user_pt_regs_t` for the build target.

## Risks and Test Signals
Risks include incomplete arch coverage, misspelled target macros, and generic fallback hiding a target-specific register layout need. Test signals are arch matrix preprocessing and BPF program builds that access expected register fields.
