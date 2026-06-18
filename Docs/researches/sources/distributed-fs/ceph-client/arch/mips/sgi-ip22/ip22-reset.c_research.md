# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-reset.c

Purpose: IP22 restart, halt, power button, panic LED, and poweroff handling. It emulates IRIX-like front-panel shutdown behavior.

Important APIs and control flow: `_machine_restart`, `_machine_halt`, and `pm_power_off` are set in `reboot_setup()`. `panel_int()` handles front-panel interrupts, debounces power-button state, and calls `power_button()`. `power_button()` signals init through `kill_cad_pid(SIGINT, 1)`, starts LED blinking, and arms a forced poweroff timer. `panic_event()` switches to faster blinking. `sgi_machine_power_off()` programs RTC watchdog/alarm state and writes panel power bits in an infinite loop.

State, persistence, and integration: state includes timers, `machine_state`, IOC reset shadow bits, panic notifier registration, and front-panel IRQ ownership. Dependencies include `sgioc`, `sgint`, `hpc3c0`, DS1286 RTC registers, and MIPS reboot hooks. Risks include timer-driven poweroff races, no graceful halt if firmware unavailable, FullHouse LED caveat, and direct infinite loops. Test signals are reboot, halt to ARCS, power button shutdown, panic LED blink, and forced timeout poweroff.
