# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_exit.c

Purpose: This file dispatches traps returned from guest execution. It handles G-stage page faults, unprivileged guest memory instruction reads, redirecting exceptions back into the guest, SBI ecalls, virtual instruction traps, MMIO faults, debug exits, and diagnostic logging for unexpected errors.

Important APIs/types/functions: `gstage_page_fault` resolves guest page faults to memory-slot mappings or MMIO emulation. `kvm_riscv_vcpu_unpriv_read` uses HLV/HLVX instructions under a temporary trap vector to safely read guest memory or instructions. `kvm_riscv_vcpu_trap_redirect` synthesizes guest VS exception state. `vcpu_redirect` redirects only when the trap came from virtual supervisor mode. `kvm_riscv_vcpu_exit` is the top-level trap dispatcher.

Control flow: G-stage faults reconstruct the fault GPA from `htval` and `stval`, look up a memslot/HVA, route invalid or write-protected accesses to MMIO load/store emulation, or call `kvm_riscv_mmu_map` to populate G-stage PTEs. Trap dispatch ignores host interrupts, increments PMU firmware counters and stats for selected guest exceptions, redirects guest-visible faults when `HSTATUS.SPV` is set, invokes virtual instruction emulation for virtual instruction faults, calls SBI emulation for supervisor ecalls, and exits to userspace on breakpoints.

State and persistence: Redirecting a trap mutates VSSTATUS, VSCAUSE, VSTVAL, VSEPC, guest `sepc`, and guest privilege bits so the guest resumes at its exception vector. MMU mapping persists in G-stage page tables. No long-lived file-local state is kept.

Dependencies and integration points: It depends on CSR accessors, hypervisor load instructions from `insn-def.h`, MMU mapping, MMIO/instruction emulation in `vcpu_insn.c`, SBI emulation, PMU firmware counters, and the vCPU run loop.

Risks and test signals: Fault GPA reconstruction and transformed instruction handling are architecture-sensitive. Trap redirection must preserve SPP/SPIE/SIE semantics exactly. Tests should cover guest page faults mapping RAM, MMIO load/store fallback, instruction fetch faults while decoding trapped instructions, illegal/misaligned/access redirects, SBI exits, breakpoint debug exits, and error logging for unsupported traps.
