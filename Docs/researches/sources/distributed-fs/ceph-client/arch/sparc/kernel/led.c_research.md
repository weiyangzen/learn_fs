# sources/distributed-fs/ceph-client/arch/sparc/kernel/led.c

Purpose: Provides a small load/user-controlled front-panel LED driver for SPARC systems through AUXIO and an optional `/proc/led` interface.

Important APIs/types/functions: `led_toggle()` reads `get_auxio()` and updates `AUXIO_LED` through `set_auxio()`. `led_blink()` toggles the LED and reschedules a global timer either by load average or a user-selected interval. With procfs enabled, `led_proc_show()`, `led_proc_open()`, and `led_proc_write()` expose state and commands: `on`, `toggle`, numeric interval seconds, `load`, and any other input as off. `led_init()` sets up the timer and proc entry; `led_exit()` removes the proc entry and deletes the timer.

Control flow: Module initialization registers `/proc/led` and arms no timer by default. Writes delete any active blink timer before changing state so manual `on`/off commands persist. Numeric or `load` commands set `led_blink_timer_timeout` and call `led_blink()` to start repeated toggles.

State and persistence: State is a global `timer_list`, timeout value, and physical AUXIO LED bit. No state persists beyond module lifetime. User writes are copied through `memdup_user_nul()` and truncated to eight bytes.

Dependencies and integration points: It depends on `asm/auxio.h`, procfs, timers, jiffies, load average `avenrun`, and module init/exit infrastructure.

Risks and test signals: Timer/proc races are mitigated with `timer_delete_sync()` on writes and exit, but command parsing is intentionally simple. Tests include proc read/write of every command, load-based blinking, module unload while blinking, AUXIO hardware access, and builds without `CONFIG_PROC_FS`.
