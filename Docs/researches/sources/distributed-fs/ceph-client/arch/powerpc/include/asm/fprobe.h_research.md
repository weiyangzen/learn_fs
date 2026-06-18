## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fprobe.h

Purpose: adapts generic fprobe support to PowerPC address layout.

Important APIs/types/functions: includes `asm-generic/fprobe.h` and, on 64-bit, overrides `FPROBE_HEADER_MSB_PATTERN` to `PAGE_OFFSET & ~FPROBE_HEADER_MSB_MASK`.

Control flow: no runtime control flow. Compile-time constants influence fprobe header/address validation.

State and persistence: no state.

Dependencies and integration: integrates generic fprobe instrumentation with PowerPC kernel virtual address high bits.

Risks and test signals: wrong MSB pattern can reject valid fprobe targets or accept invalid ones. Test signals include fprobe/ftrace selftests on PPC64, kprobe/fprobe coexistence, and address validation for kernel text and modules.
