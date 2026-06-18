# sources/distributed-fs/ceph-client/drivers/pcmcia/sa1111_neponset.c

Purpose: Provides Assabet Neponset board-specific PCMCIA power control using a Maxim MAX1600 power switch while delegating socket status and SA1111 register control to generic code.

Important APIs and functions: `neponset_pcmcia_hw_init()` initializes a MAX1600 channel for each socket and stores it in `skt->driver_data`. `neponset_pcmcia_configure_socket()` calls `sa1111_pcmcia_configure_socket()` and then `max1600_configure()`. `pcmcia_neponset_init()` installs SA11xx timing callbacks and adds two sockets.

Control flow: The generic SA1111 probe dispatches here for Assabet. Per-socket init chooses MAX1600 channel A for socket 0 and channel B for socket 1, both in low-code mode. Configure applies SA1111 reset/float/wait state first, then power-switch Vcc/Vpp.

State and persistence: MAX1600 channel object persists in `driver_data`; voltage output state persists in the power switch and SA1111 PCCR registers.

Dependencies and integration points: Depends on `max1600.h`, SA1111 generic helpers, SA11xx resource/timing glue, and Assabet machine dispatch.

Risks: The comments describe asymmetric VPP wiring: socket B is CF and VPP lines are grounded. The code relies on `max1600_configure()` to reject or translate unsupported combinations. Ordering between SA1111 and power switch writes should be preserved.

Test signals: Assabet/Neponset probe, MAX1600 channel initialization for both sockets, Vcc/Vpp transitions including CF socket limitations, and card detect/status via SA1111 common code.
