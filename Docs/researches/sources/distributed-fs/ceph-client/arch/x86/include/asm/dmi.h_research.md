
# sources/distributed-fs/ceph-client/arch/x86/include/asm/dmi.h

Purpose: x86 DMI allocation and mapping helpers for early firmware table scanning.

Important APIs and control flow: `dmi_alloc()` allocates from early `extend_brk()` with integer alignment. Remap macros map early DMI through `early_memremap`/`early_memunmap` and later DMI through `memremap(..., MEMREMAP_WB)`/`memunmap`.

State, dependencies, and risks: state is early boot brk allocation and DMI mapped memory. Dependencies include setup/early memory mapping APIs. Risks include allocating before memory management is ready, mapping firmware tables with wrong attributes, and lifetime mismatch between early and late mappings. Test signals are DMI scan boot logs, DMI-based quirk activation, and early boot memory tests.
