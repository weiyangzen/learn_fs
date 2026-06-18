# sources/distributed-fs/ceph-client/arch/arm/kernel/v7m.c

Purpose: supplies ARMv7-M restart support. `armv7m_restart` writes the SCB AIRCR key plus SYSRESETREQ after data synchronization barriers.

Control flow is a short reboot path: flush outstanding memory operations with `dsb`, write `V7M_SCB_AIRCR_VECTKEY | V7M_SCB_AIRCR_SYSRESETREQ` to the system control block, then issue another `dsb`. There is no local state or allocation. Dependencies are the ARMv7-M SCB base definitions, raw MMIO write helpers, and the generic reboot path that installs this restart callback. Risks are wrong SCB base mapping or missing reset response from platform hardware. Test signals are reboot tests on ARM_SINGLE_ARMV7M systems and observation that the CPU resets rather than returning.
