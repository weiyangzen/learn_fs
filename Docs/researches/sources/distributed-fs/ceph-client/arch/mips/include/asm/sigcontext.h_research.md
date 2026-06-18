<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sigcontext.h

Purpose: Connects kernel-private MIPS signal context handling to the UAPI signal context and defines a 32-bit compatibility `sigcontext32` layout for compat signal frames.

Important APIs/types/functions: Includes `<uapi/asm/sigcontext.h>` and defines `struct sigcontext32` with 32-bit register, FP register, FPC CSR, used-math, DSP, and reserved fields for 32-bit user ABI compatibility on a 64-bit kernel.

Control flow: Signal setup and restore code uses the structure when copying user signal frames for compat tasks. No functions are implemented here.

State and persistence: The structure serializes per-thread CPU/FPU/DSP state into user memory during signal delivery and reads it back during sigreturn. Persistence is the user-visible signal frame ABI.

Dependencies and integration points: Depends on the UAPI MIPS sigcontext definition and is included by `asm/signal.h` and arch signal code.

Risks: Field order and width are ABI-sensitive; changing the layout breaks existing 32-bit user programs and sigreturn. Padding/reserved fields must remain stable.

Test signals: Compat signal delivery/sigreturn tests, ptrace/register-state tests around signals, FP/DSP signal context tests, and 32-bit userspace on 64-bit MIPS are key signals.

Source read size: 37 lines, 1060 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sigcontext.h -->
