# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/kexec.h

Purpose: resets Book3S64 security and breakpoint-related SPR state before a kexec transition.

Important APIs/types/functions: defines `reset_sprs()` as the architecture hook. It clears `SPRN_AMR` and `SPRN_UAMOR` on ISA 2.06 CPUs, `SPRN_IAMR` and CIABR on ISA 2.07S CPUs, and `SPRN_DEXCR` plus `SPRN_HASHKEYR` on ISA 3.1 CPUs. CIABR is cleared either directly in HV mode or through `plpar_set_ciabr(0)`.

Control flow: `reset_sprs()` tests CPU feature bits in increasing ISA order, writes the relevant SPRs to zero, then issues `isync()` before the kexec reset path continues.

State and persistence: the function clears live per-CPU SPR state so AMR/IAMR, CIABR, DEXCR, and HASHKEYR settings do not leak into the next kernel.

Dependencies and integration points: includes `plpar_wrappers.h` and uses `cpu_has_feature()`, `mtspr()`, SPR constants, and PAPR CIABR hypervisor calls. It integrates with the generic kexec architecture reset hook.

Risks: missing a security-sensitive SPR could leave stale access-control, breakpoint, or execution-control state after kexec. CIABR clearing must use the hypervisor call when not in HV mode.

Test signals: kexec and kdump tests across ISA 2.06, 2.07S, and 3.1 systems; verify AMR/IAMR/CIABR/DEXCR/HASHKEYR are reset before entering the new kernel.
