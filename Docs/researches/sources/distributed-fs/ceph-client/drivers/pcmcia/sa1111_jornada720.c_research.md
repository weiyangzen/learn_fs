# sources/distributed-fs/ceph-client/drivers/pcmcia/sa1111_jornada720.c

Purpose: Provides HP Jornada 720 board-specific SA1111 PCMCIA power GPIO control.

Important APIs and functions: `jornada720_pcmcia_hw_init()` allocates per-socket GPIO descriptor storage and gets `s0-power`/`s1-power` plus `s0-3v`/`s1-3v`. `jornada720_pcmcia_configure_socket()` maps requested Vcc/Vpp to GPIO values and calls `sa1111_pcmcia_configure_socket()`. `pcmcia_jornada720_init()` installs SA11xx timing callbacks and calls `sa1111_pcmcia_add()`.

Control flow: Init adjusts SA11x0 GPIO edge register `GRER`, then adds two sockets. Configure handles socket 0 with separate 3.3V vs 5V GPIO state; socket 1 treats 3.3V and 5V the same. Unsupported independent Vpp returns `-EPERM`. On success, SA1111 register state is updated before GPIO outputs are written as an array.

State and persistence: Per-socket `jornada720_data` is stored in `skt->driver_data`. GPIO power and voltage-select outputs persist until reconfigured or device removal.

Dependencies and integration points: Depends on SA1111 generic functions, SA11xx timing glue, board GPIO descriptors, and `machine_is_jornada720()` dispatch in `sa1111_generic.c`.

Risks: Socket 1 voltage behavior is uncertain per source comments. Power sequencing order may matter because SA1111 state is applied before board GPIOs. The direct `GRER` manipulation is legacy board-specific global state.

Test signals: Jornada720 probe, GPIO descriptor lookup for both sockets, Vcc 0/33/50 transitions, Vpp rejection path, card operation on both slots, and correct status/IRQ behavior via SA1111 common code.
