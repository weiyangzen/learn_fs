# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-reset.c

Purpose: SGI O2 restart, halt/poweroff, power-button shutdown preparation, and panic LED handling.

Important APIs and control flow: `ip32_poweroff()` dynamically obtains `ds1685_rtc_poweroff`, optionally requests the RTC module, invokes it with `ip32_rtc_device`, and never returns. `ip32_machine_restart()` writes `CRIME_CONTROL_HARD_RESET`. `ip32_prepare_poweroff()` handles power button shutdown, signals init, starts red LED blinking, and arms a forced poweroff timer. `panic_event()` turns off green LED and starts faster red blink. `ip32_reboot_setup()` initializes LEDs, installs restart/halt/poweroff hooks, sets up the blink timer, and registers panic notifier.

State, persistence, and integration: state includes timers, LED state via MACE misc register, panic/shutdown flags, machine hooks, panic notifier, and RTC poweroff callback linkage. Dependencies include CRIME/MACE mappings, RTC platform device, module symbol lookup, and `kill_cad_pid()`. Risks include dependency on RTC driver/module for actual poweroff, timer races, and dynamic symbol failure causing infinite spin. Test signals are hard reset, front-button shutdown, panic LED blinking, RTC poweroff, and forced timeout behavior.
