
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/idle.c

Purpose: provides PowerNV CPU idle, stop/nap/sleep/winkle entry and wakeup handling, deep-state register save/restore, CPU hotplug offline idle, and device-tree parsing of OPAL idle states.

Important APIs/functions/state: exports `pnv_get_supported_cpuidle_states()`, `pnv_power9_force_smt4_catch()`, `pnv_power9_force_smt4_release()`, `pnv_program_cpu_hotplug_lpcr()`, and `pnv_cpu_offline()`. Core paths are `power7_idle_insn()`, `power9_idle_stop()`, `power10_idle_stop()`, `arch300_idle_type()`, `validate_psscr_val_mask()`, `pnv_arch300_idle_init()`, `pnv_parse_cpuidle_dt()`, and `pnv_init_idle_states()`. Global state includes discovered `pnv_idle_states`, supported flags, default/deepest PSSCR values, TB and SPR loss thresholds, and Power7 fastsleep workaround flags.

Control flow: subsystem init initializes PACA idle state fields, parses `/ibm,opal/power-mgt`, validates properties, calculates supported states, selects platform `ppc_md.power_save`, and programs OPAL stop-api SPR restoration for deep states. Power7/8 paths save per-core/subcore/thread SPRs for winkle, manage fastsleep workaround apply/undo, track idle threads via PACA bit fields, resync timebase after loss, and restore SLB/SPR state. POWER9/10 paths construct PSSCR, enter ISA 3.0 stop, use PLS to detect SPR/TB loss, restore core/thread registers, handle HMI wakeups, and coordinate KVM stop avoidance for SMT4 workarounds.

State and persistence: runtime state lives in PACA fields, global idle-state arrays, sysfs attribute `fastsleep_workaround_applyonce`, and OPAL stop-api register programming. No filesystem persistence exists.

Dependencies and integration points: depends on OPAL idle state DT properties, stop-api calls, PowerPC idle assembly helpers, PACA, cpuidle disable policy, KVM HV fields, subcore sibling masks, runlatch, doorbells, HMI real-mode handling, SLB restore, and CPU hotplug.

Risks: real-mode idle code has strict MMU/interrupt assumptions. Incorrect state-loss thresholds can skip required SPR or timebase restoration. POWER10 deep loss handling is intentionally incomplete and deep context-loss states are skipped. Fast sleep workaround sysfs changes affect all cores. KVM `dont_stop` ordering is security-critical because a thread may be switched to a guest context.

Test signals: DT parsing on POWER8/9/10/11, platform idle entry/exit under interrupt load, timebase continuity, CPU offline/online, KVM HV guest coexistence, fastsleep workaround sysfs, HMI wake handling, and suspend-like deep state stress.
