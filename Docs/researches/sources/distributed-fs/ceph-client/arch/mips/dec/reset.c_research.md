# sources/distributed-fs/ceph-client/arch/mips/dec/reset.c

Purpose: implements DECstation restart, halt, power-off, and halt-button interrupt behavior by returning control to PROM.

Important APIs: `dec_machine_restart()`, `dec_machine_halt()`, and `dec_machine_power_off()` all call `back_to_prom()`, which jumps to ROM address `0x1fc00000` via KSEG1. `dec_intr_halt()` is an IRQ handler that halts the machine.

State and integration: reboot hooks are installed from `dec/setup.c`, and the halt interrupt may be requested if the machine exposes one.

Risks and test signals: DECstations lack software power-off, so power-off is equivalent to PROM return. Test halt button IRQ routing and reboot/halt paths on supported machines.
