# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/shmobile/pm.c

Purpose: prepares and invokes SH-Mobile low-power entry code from on-chip RAM, with notifier hooks and board-supplied self-refresh snippets.

Important APIs and control flow: `sh_mobile_call_standby()` calls pre-sleep notifiers, optionally flushes caches for MMU-affecting modes, jumps into copied on-chip standby code, then calls post-sleep notifiers. `sh_mobile_register_self_refresh()` populates a `struct sh_sleep_data` at `RAM_BASE`, copies common enter code, board pre/post self-refresh code, and common resume code, then advertises supported flags. `sh_pm_enter()` selects sleep or standby-self-refresh for suspend-to-mem and calls standby. `sh_pm_init()` registers platform suspend operations.

State, dependencies, and risks: state lives in on-chip memory at `RAM_BASE`, global notifier chains, and `sh_mobile_sleep_supported`. Dependencies include `sleep.S` symbols, board-specific self-refresh code, cache flushing, BL bit handling, and fixed SH-Mobile register addresses. Risks include overrun of the 0x600-byte code/data budget, SoC-specific RAM base mismatch, stale cache/MMU state, and notifier ordering. Test signals are suspend-to-RAM cycles, cpuidle deep-state entry, and board self-refresh resume reliability.
