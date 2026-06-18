# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/bpf_perf_event.h

Purpose: defines the PowerPC register type used by BPF programs attached to perf events.

Important APIs/types/functions: includes `<asm/ptrace.h>` and typedefs `struct user_pt_regs` to `bpf_user_pt_regs_t`.

Control flow: no runtime logic.

State and persistence: no state. It defines a type contract between BPF helpers and PowerPC pt_regs layout.

Dependencies and integration points: integrates BPF perf event programs with PowerPC user register views.

Risks: if `user_pt_regs` layout changes, BPF program expectations and verifier/context access must remain consistent.

Test signals: BPF perf-event selftests on PowerPC, compile checks for BPF programs referencing `bpf_user_pt_regs_t`, and pt_regs field access validation.
