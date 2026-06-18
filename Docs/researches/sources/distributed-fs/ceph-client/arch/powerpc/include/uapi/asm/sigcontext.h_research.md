<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/sigcontext.h

Purpose: Defines PowerPC signal context layout, including 64-bit register, FP, VMX, and VSX save areas.

Important APIs/types/functions: `struct sigcontext` with signal metadata, handler, old mask, regs pointer, 64-bit `gp_regs`, `fp_regs`, vector-register pointer, and `vmx_reserve` backing storage.

Control flow: Signal delivery fills this context in the user signal frame; `sigreturn` reads it back to restore interrupted CPU state. On ppc64 VMX/VSX data is aligned through the `v_regs` pointer into reserved storage.

State and persistence: The user signal frame is persistent until handler return and serializes register state.

Dependencies and integration points: Depends on ptrace and ELF register definitions. Integrated by signal delivery, ptrace-compatible register layouts, and libc signal trampolines.

Risks: Signal frame layout is strict ABI. Vector/VSX reserve sizing and alignment must remain compatible with old userspace.

Test signals: Signal delivery/sigreturn tests with FP/VMX/VSX, altstack tests, GDB signal-frame unwinding, and ppc64 layout checks.

Source read size: 92 lines, 4444 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/sigcontext.h -->
