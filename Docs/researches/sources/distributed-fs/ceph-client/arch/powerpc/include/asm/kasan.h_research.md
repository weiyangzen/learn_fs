# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kasan.h

Purpose: Defines PowerPC KASAN shadow memory layout, early initialization hooks, and address conversion helpers.

Important APIs, types, and functions: Provides architecture KASAN constants/macros for shadow offsets and declares initialization helpers for mapping KASAN shadow regions, with config-dependent stubs when KASAN is disabled or unsupported.

Control flow: Early boot initializes shadow mappings before broad memory use. KASAN instrumentation converts kernel addresses to shadow addresses and checks poison state.

State and persistence: Shadow memory is runtime kernel memory mirroring poisoned/unpoisoned state. No disk persistence.

Dependencies and integration points: Depends on MMU/page-table setup, memory layout, and generic KASAN instrumentation.

Risks: Shadow offset or mapping mistakes can fault during early boot or hide memory bugs. Interaction with vmalloc/modules and radix/hash layouts is config-sensitive.

Test signals: KASAN boot, slab/stack/global out-of-bounds reports, vmalloc/module shadow coverage, early memory access, and builds with KASAN disabled.
