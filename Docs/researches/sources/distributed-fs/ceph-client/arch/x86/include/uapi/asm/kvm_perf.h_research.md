<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm_perf.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm_perf.h

Purpose: Provides x86 KVM perf trace decoding names and includes VMX/SVM/KVM exit-reason definitions needed by perf tooling.

Important APIs/types/functions: `DECODE_STR_LEN`, `VCPU_ID`, `KVM_ENTRY_TRACE`, `KVM_EXIT_TRACE`, and `KVM_EXIT_REASON`.

Control flow: Perf tooling uses these constants to locate tracepoints and decode exit-reason fields using included VMX/SVM definitions.

State and persistence behavior: No runtime state. Tracepoint names are an observability ABI.

Dependencies and integration points: Includes `asm/svm.h`, `asm/vmx.h`, and `asm/kvm.h`; integrates with perf, ftrace, KVM tracepoints, and virtualization performance analysis.

Risks and test signals: Risks are tracepoint name drift or exit-reason decode mismatch. Test `perf kvm` on Intel and AMD hosts, KVM entry/exit traces, and decoding of VMX/SVM exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm_perf.h -->
