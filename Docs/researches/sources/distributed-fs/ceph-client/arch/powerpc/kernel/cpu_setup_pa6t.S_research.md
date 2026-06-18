<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_pa6t.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_pa6t.S

Purpose: Performs minimal PA6T setup/restore for hypervisor-capable operation.

Important APIs/types/functions: `__setup_cpu_pa6t` and `__restore_cpu_pa6t` share one implementation.

Control flow: The routine checks MSR HV mode and returns if not privileged enough; otherwise it sets selected HID5 bits and LPCR bits before returning.

State and persistence: Mutates PA6T HID5 and LPCR special-purpose registers when running in HV mode.

Dependencies and integration points: Depends on PA6T SPR definitions and CPU setup dispatch for Book3S 64-bit PA Semi systems.

Risks: Only safe in HV mode. Incorrect HID5/LPCR bits can alter interrupt or partition behavior.

Test signals: PA6T boot/restore build coverage, HV-mode detection tests where hardware is available, and suspend/resume smoke tests.

Source read size: 31 lines, 609 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cpu_setup_pa6t.S -->
