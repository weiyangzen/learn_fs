# sources/distributed-fs/ceph-client/arch/mips/include/asm/mipsregs.h

Purpose: Central MIPS CP0/CP1 register, bitfield, instruction, and TLB operation header. It is a foundational architecture interface used across exception handling, MMU, cache, FPU, virtualization, DSP, and CPU feature code.

Important APIs/types/functions: Defines CP0 register names/selects, EntryLo/PageMask/PageGrain/EntryHi/status/cause/config/watch/perf/MAAR/EBase/segmentation/page-walker/guest-control/CDMM/FPU constants, exception codes, and ISA mode helpers. Inline/macro APIs include `mm_insn_16bit()`, raw instruction emitters, assembler macro generators, `tlbinvf()`, R10000 performance counter helpers, generic CP0 read/write primitives for 32/64/ulong and high-half XPA access, hundreds of `read_c0_*`/`write_c0_*` and guest `read_gc0_*`/`write_gc0_*` wrappers, CP1 control access, DSP accumulator/control access, TLB operations, guest TLB operations, set/clear/change builders, and `get_ebase_cpunum()`.

Control flow, state, and persistence: Most helpers emit inline assembly to read/write processor control registers, with special paths for 32-bit kernels accessing 64-bit CP0 registers under local IRQ disable. TLB helpers require callers to handle hazards. Persistent state is CPU control-register, TLB, guest CP0, FPU, DSP, and page-walker hardware state.

Dependencies and integration: Includes hazards and ISA revision support. It is consumed by nearly all MIPS low-level code: traps, context switch, KVM/VZ, perf, cache/TLB management, FPU/MSA, CPU probing, and platform setup.

Risks and test signals: This header is high blast radius. Risks include wrong register select, missing hazard barriers, fallback instruction encoding mistakes, 32/64-bit split ordering, microMIPS encoding mismatches, and unsafe TLB operations. Test with broad MIPS defconfig builds, boot on multiple ISA revisions, KVM/VZ guest tests, perf/FPU/DSP/MSA tests, TLB stress, and assembler fallback configurations.
