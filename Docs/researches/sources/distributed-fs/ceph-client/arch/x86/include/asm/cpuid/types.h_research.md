
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpuid/types.h

Purpose: CPUID register containers and parsed leaf 0x2 descriptor type definitions.

Important APIs and control flow: defines `struct cpuid_regs`, `enum cpuid_regs_idx`, selected leaf constants, `union leaf_0x2_regs`, packed cache/TLB descriptor type enums, `struct leaf_0x2_table`, the external `cpuid_0x2_table[256]`, and `TLB_0x63_2M_4M_ENTRIES`. Static assertions keep packed enum widths at one byte.

State, dependencies, and risks: state is external descriptor table data and caller-filled CPUID register unions. Dependencies include Linux integer types and build assertions. Risks include descriptor type overlap, enum packing differences under sparse/checker, and table entries drifting from Intel descriptor meanings. Test signals are CPUID descriptor parser tests, cache/TLB info output, and compile-time assertions.
