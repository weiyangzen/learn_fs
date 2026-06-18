# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/headsmp-a9.S

Purpose: Cortex-A9 secondary CPU entry point for MVEBU Armada 375/38x style systems.

Important APIs/types/functions: Defines `mvebu_cortex_a9_secondary_startup`.

Control flow: The secondary entry fixes BE8 endianness when needed, calls `armada_38x_scu_power_up` to power/enable SCU-side CPU state, then branches to generic `secondary_startup`.

State and persistence: No data state. Hardware state is whatever `armada_38x_scu_power_up` changes before the generic secondary path.

Dependencies and integration points: Depends on `pmsu_ll.S` providing `armada_38x_scu_power_up`, ARM assembler conventions, and C SMP code programming this label as the boot address.

Risks: If the SCU power-up helper is missing or wrong, secondary CPUs may jump into Linux without required coherency/power state. The label must remain suitable as an early secondary entry point.

Test signals: Boot SMP on Armada 375/38x/39x Cortex-A9 systems and verify all secondary CPUs enter the kernel.
