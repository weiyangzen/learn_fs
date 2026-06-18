# sources/distributed-fs/ceph-client/arch/mips/cobalt/reset.c

Purpose: implements Cobalt halt and restart hooks plus a power-off LED trigger.

Important APIs: `ledtrig_power_off_init()` registers trigger `"power-off"`. `cobalt_machine_halt()` activates the trigger, disables local IRQs, and waits forever using `cpu_wait()` if available. `cobalt_machine_restart()` writes reset value `0x0f` to MMIO reset port `0x1c000000`, then falls back to halt.

State and integration: the LED trigger persists in the LED subsystem. Reboot hooks are installed from `setup.c`.

Risks and test signals: restart depends on the fixed reset port and value. Halt should light the configured LED on RaQ systems; reboot should not return.
