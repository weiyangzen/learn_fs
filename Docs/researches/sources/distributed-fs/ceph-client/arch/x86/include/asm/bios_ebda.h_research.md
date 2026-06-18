
# sources/distributed-fs/ceph-client/arch/x86/include/asm/bios_ebda.h

Purpose: access and reservation hooks for BIOS Extended BIOS Data Area and legacy BIOS memory corruption checks.

Important APIs and control flow: `get_bios_ebda()` reads the real-mode segmented EBDA pointer at physical `0x40e`, shifts it by four to compute a physical address, and returns zero when absent. `reserve_bios_regions()` is declared for boot reservation. Optional corruption-check functions are real declarations under `CONFIG_X86_CHECK_BIOS_CORRUPTION` and no-op stubs otherwise.

State, dependencies, and risks: state is firmware-provided low-memory data and kernel reservations. Dependencies include early physical mapping through `phys_to_virt`. Risks include bogus BIOS pointers, early-memory access before mappings are stable, and false confidence from optional corruption checks. Test signals are boot on legacy BIOS systems, memory reservation logs, and corruption-check configuration builds.
