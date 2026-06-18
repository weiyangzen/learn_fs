<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/reboot_fixups.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/reboot_fixups.h

Purpose: declares `mach_reboot_fixups()`, the x86 hook for platform-specific reboot quirks.

Control flow and state: reboot code can invoke the function before reset to apply chipset or machine-specific workarounds; state is owned by implementation-specific fixups. Dependencies are reboot flow and platform quirk tables. Risks are regressions on old machines that require special reset sequencing. Test signals include reboot testing on affected systems and compile/link coverage when fixup support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/reboot_fixups.h -->
