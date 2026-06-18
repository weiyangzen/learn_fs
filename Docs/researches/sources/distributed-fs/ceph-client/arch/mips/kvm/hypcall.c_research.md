## sources/distributed-fs/ceph-client/arch/mips/kvm/hypcall.c

Purpose: Handles MIPS KVM hypercall instruction recognition and dispatch.

Important APIs, types, and functions: `kvm_mips_emul_hypcall()` decodes the hypercall code from the instruction and returns `EMULATE_HYPERCALL` only for code 0. `kvm_mips_handle_hypcall()` reads the hypercall number from `v0` and up to four arguments from `a0`-`a3`, then calls `kvm_mips_hypercall()`. The current dispatcher reports `-KVM_ENOSYS` in `v0`.

Control flow: Emulation identifies whether a decoded instruction should become a hypercall exit/handler path. Handling extracts ABI registers, invokes the local dispatcher, and returns `RESUME_GUEST`; no userspace exit is produced for unimplemented calls.

State and persistence: Only VCPU GPR state is read and `gprs[2]` (`v0`) is overwritten with the return value. No persistent hypercall state exists.

Dependencies and integration points: Includes KVM host and paravirtual headers. It is called by the instruction emulation/guest-exit backend when a hypercall instruction is encountered.

Risks: Hypercall surface is intentionally skeletal; all numbers are unimplemented. If future calls are added, ABI width/sign handling and userspace compatibility need careful definition.

Test signals: Hypercall code 0 returns `-KVM_ENOSYS`; nonzero instruction code fails emulation; argument registers remain intact except return register.
