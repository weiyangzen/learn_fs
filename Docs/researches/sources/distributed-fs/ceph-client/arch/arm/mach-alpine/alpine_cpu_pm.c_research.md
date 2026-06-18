# sources/distributed-fs/ceph-client/arch/arm/mach-alpine/alpine_cpu_pm.c

Purpose: low-level Alpine CPU power-management and wakeup service. It initializes sysfabric and CPU-resume register access and exposes `alpine_cpu_wakeup`.

Control flow: `alpine_cpu_pm_init` finds a syscon regmap and maps `al,alpine-cpu-resume`, then validates a magic watermark. `alpine_cpu_wakeup` writes a physical resume address into the per-CPU resume structure and clears the sysfabric power-control register for that CPU. Persistent state includes `al_sysfabric`, `al_cpu_resume_regs`, and `wakeup_supported`. Dependencies are DT compatible nodes, syscon/regmap, memory-mapped resume registers, and firmware that honors the resume structure. Risks are missing or invalid watermark, 32-bit resume address assumptions, and no wakeup support returning `-ENOSYS`. Test signals include SMP secondary boot, watermark validation logs/behavior, and regmap write success.
