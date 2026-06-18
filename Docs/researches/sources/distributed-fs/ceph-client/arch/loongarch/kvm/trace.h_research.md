# sources/distributed-fs/ceph-client/arch/loongarch/kvm/trace.h

Purpose: defines LoongArch KVM tracepoints for guest transitions, exits, GSPR instructions, auxiliary FPU/vector state, IOCSR accesses, and VPID changes.

Important APIs, types, and functions: event classes `kvm_transition` and `kvm_exit`; events `kvm_enter`, `kvm_reenter`, `kvm_out`, `kvm_exit_idle`, `kvm_exit_cache`, `kvm_exit_cpucfg`, `kvm_exit_csr`, `kvm_exit`, `kvm_exit_gspr`, `kvm_aux`, `kvm_iocsr`, and `kvm_vpid_change`. It sets `TRACE_SYSTEM kvm` and includes `trace/define_trace.h`.

Control flow: tracepoint macros define payload fields, fast assignment, symbolic printers, and trace include path/file. `vcpu.c` creates tracepoints by defining `CREATE_TRACE_POINTS` before including this header.

State and persistence: no runtime state beyond trace buffers when enabled. Tracepoint ABI names and fields are observable by tracing tools.

Dependencies and integration points: consumed by `exit.c`, `main.c`, and `vcpu.c`; integrates with Linux ftrace/perf trace infrastructure and generic KVM event namespace.

Risks: tracepoint field or name changes can break tooling. Include guards and `TRACE_HEADER_MULTI_READ` placement must remain compatible with trace generation.

Test signals: successful trace header generation, `tracefs` event availability, and trace output during guest run, exits, IOCSR operations, and VPID changes.
