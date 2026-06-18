# sources/distributed-fs/ceph-client/drivers/cpuidle/Kconfig

Purpose: defines top-level CPU idle configuration symbols, governor choices, architecture submenus, and the haltpoll driver option.

Important APIs and symbols: `CPU_IDLE` enables the generic framework and selects default governors based on tick configuration. Governor symbols include `CPU_IDLE_GOV_LADDER`, `CPU_IDLE_GOV_MENU`, `CPU_IDLE_GOV_TEO`, and `CPU_IDLE_GOV_HALTPOLL`. `DT_IDLE_STATES` and `DT_IDLE_GENPD` enable DT idle-state and generic PM domain parsing support. Architecture submenus source ARM, MIPS, POWERPC, and RISC-V Kconfig fragments. `HALTPOLL_CPUIDLE` depends on x86 KVM guests and selects the haltpoll governor. `ARCH_NEEDS_CPU_IDLE_COUPLED` marks platforms needing coupled idle support.

Control flow and state: Kconfig has no runtime state but controls which core objects, governors, and platform drivers build. Defaults bias CPU idle on for ACPI and pSeries and select a suitable governor based on `NO_HZ`/`NO_HZ_IDLE`.

Dependencies and integration points: integrates with arch-specific Kconfig files under `drivers/cpuidle/`, generic PM domains, KVM guest hints, and Makefile object selection.

Risks and test signals: risks include wrong default governor selection for unusual tick configurations, haltpoll only being available for x86 KVM guests, and architecture submenu symbols hiding platform drivers if arch dependencies are not met. Test signals are expected `.config` symbol selection, correct object inclusion in `drivers/cpuidle/Makefile`, and boot logs showing the intended cpuidle governor/driver.
