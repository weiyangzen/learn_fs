# sources/distributed-fs/ceph-client/arch/microblaze/kernel/reset.c

Purpose: supplies MicroBlaze machine shutdown, halt, poweroff, and restart hooks.

Important APIs and state: `machine_shutdown()`, `machine_halt()`, and `machine_power_off()` log and spin forever. `machine_restart(char *cmd)` calls restart notifiers via `do_kernel_restart()`, waits one second, then logs failure and spins.

Control flow: there is no hardware reset sequence here; restart depends entirely on registered restart handlers.

State and persistence: no persistent state, but successful restart is delegated to notifier infrastructure.

Dependencies and integration: used by reboot/poweroff core and by MMU init fatal checks that call `machine_restart(NULL)`.

Risks and test signals: without a platform restart handler, reboot hangs after emergency log. Test reboot with and without a registered restart notifier and ensure watchdog/platform reset drivers integrate.
