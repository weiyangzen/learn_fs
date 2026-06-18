# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/idle.c

Purpose: PA6T idle-mode selection and system-reset wake handler for power-saving modes.

Important APIs and control flow: `modes` maps `spin` and `doze` to assembly entry points; early parameter `idle=` selects one. `pasemi_idle_init` installs `pasemi_system_reset_exception` and `ppc_md.power_save`, forcing spin when cpufreq support is absent. The reset exception detects wake causes from `SRR1_WAKEMASK`, redirects return IP to link when waking from power save, re-arms the decrementer for DEC wake, defers external interrupts, restores CPU astate, and marks the exception recoverable.

State, dependencies, and risks: state is `current_mode` and `ppc_md` callbacks. Dependencies include `powersave.S`, cpufreq astate helpers, system-reset exception semantics, and SMP processor IDs. Risks include incorrect return-IP handling for future sleep modes, power-saving disabled without cpufreq, and NMI-context restrictions for external wake. Test signals are idle parameter parsing, wake from decrementer/external interrupt, astate restoration, and no reset-loop on real system reset.
