# sources/distributed-fs/ceph-client/arch/riscv/kvm/trace.h

Purpose: This header defines RISC-V KVM tracepoints for guest entry and exit. It gives ftrace/perf consumers a compact view of guest PC on entry and trap CSRs on exit.

Important APIs/types/functions: `TRACE_EVENT(kvm_entry)` records `vcpu->arch.guest_context.sepc` as `pc`. `TRACE_EVENT(kvm_exit)` records `sepc`, `scause`, `stval`, `htval`, and `htinst` from `struct kvm_cpu_trap`. `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` make the tracepoint definitions instantiate from `vcpu.c`.

Control flow: `vcpu.c` defines `CREATE_TRACE_POINTS` before including this header, which instantiates the tracepoints. The run loop calls `trace_kvm_entry(vcpu)` immediately before guest entry and `trace_kvm_exit(&trap)` after returning from guest mode and restoring interrupt state.

State and persistence: The header owns no runtime state beyond the generated tracepoint descriptors. Recorded data is transient trace-buffer state managed by the Linux tracing subsystem.

Dependencies and integration points: It depends on `linux/tracepoint.h`, `struct kvm_vcpu`, and `struct kvm_cpu_trap`. It integrates with the RISC-V vCPU run loop and generic Linux trace tooling under the `kvm` trace system.

Risks and test signals: Format-string stability matters for external tracing tools. The entry print format uses `"PC: 0x016%lx"`, which may be unusual compared with `%016lx` and should be checked if trace formatting is changed. Tests should enable KVM tracepoints, run a guest, and verify entry/exit records contain expected PC and trap CSR values without instrumentation recursion.
