<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/realmode.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/realmode.h

Purpose: describes the x86 real-mode blob headers and trampoline entry data used for SMP startup, ACPI resume, BIOS/APM reboot, and encrypted-memory AP startup. Important types are `real_mode_header` and `trampoline_header`; APIs include `real_mode_size_needed()`, `set_real_mode_mem()`, `reserve_real_mode()`, `load_trampoline_pgtable()`, and `init_real_mode()`.

Control flow: boot reserves low memory for the real-mode blob, copies/relocates the blob, initializes trampoline fields such as start address, EFER/CR4, SME flags, and lock word, then AP startup/reboot/resume paths jump through those real-mode entry points.

State and persistence: global pointers and symbols reference the allocated blob, relocation table, trampoline lock, initial code/stack, optional VC handler, and architecture-specific startup symbols. State is boot/runtime low-memory state. Dependencies include realmode assembly layouts, ACPI sleep, AMD memory encryption, paging, and SMP startup. Risks are strict layout coupling with assembly, low-memory allocation mistakes, SME/SEV flag handling, and wrong trampoline page table setup. Test signals include SMP bring-up, CPU hotplug, ACPI S3 resume, reboot modes, SEV-ES AP startup, and relocation-size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/realmode.h -->
