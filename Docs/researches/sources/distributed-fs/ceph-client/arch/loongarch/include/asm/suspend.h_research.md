<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/suspend.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/suspend.h

Purpose: declares low-level LoongArch suspend/resume entry points and saved-state hooks.
Important APIs and types: exposes `loongarch_suspend_enter`/ACPI suspend glue when power management is configured.
Control flow: PM core calls architecture suspend code, which saves CPU state, enters firmware/ACPI low-power flow, then resumes through low-level restore paths.
State and persistence: state is saved in CPU/firmware-specific areas across suspend; this header only declares the interface.
Dependencies and integration: integrates with ACPI suspend, CPU context save/restore, IRQ/clock state, and platform firmware.
Risks and test signals: missing declarations or wrong prototypes break suspend builds; implementation mistakes show as resume crashes. Signals include suspend/resume cycles, CPU hotplug around suspend, and ACPI sleep-state tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/suspend.h -->
