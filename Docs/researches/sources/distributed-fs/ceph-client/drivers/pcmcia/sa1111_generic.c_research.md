# sources/distributed-fs/ceph-client/drivers/pcmcia/sa1111_generic.c

Purpose: Implements generic SA1111 companion-chip PCMCIA support. It handles status decoding, PCCR register configuration, SA1111 IRQ mapping, device enable/disable, and dispatch to board-specific power control.

Important APIs and functions: Exports `sa1111_pcmcia_socket_state()`, `sa1111_pcmcia_configure_socket()`, and `sa1111_pcmcia_add()`. The SA1111 driver entry points are `pcmcia_probe()` and `pcmcia_remove()`, registered via `sa1111_driver_register()`.

Control flow: Probe enables the SA1111 device, claims its register window, initializes sleep/float state, and calls `pcmcia_jornada720_init()` or `pcmcia_neponset_init()` depending on machine type. `sa1111_pcmcia_add()` fetches six SA1111 IRQs, installs the generic status callback into low-level ops, allocates one wrapper per socket, maps ready/card-detect/BVD IRQs for socket 0 or 1, and calls the supplied add function. Configure computes socket-specific masks but socket-independent set bits, then updates PCCR under local IRQ disable.

State and persistence: Each socket wrapper stores a common `soc_pcmcia_socket`, `struct sa1111_dev *`, and linked-list pointer in device driver data. SA1111 PCCR/PCSSR state persists in mapped hardware registers.

Dependencies and integration points: Depends on SA1111 bus APIs, common SoC PCMCIA, SA11xx timing/resource glue, and board files `sa1111_jornada720.c` and `sa1111_neponset.c`.

Risks: `sa1111_pcmcia_configure_socket()` sets PWAIT/PSE/RST/FLT bits for both sockets then masks to the target, so future bit additions must preserve this pattern. Probe only supports Jornada720 and Assabet/Neponset machine paths. IRQ index mapping is fixed and must match SA1111 hardware.

Test signals: SA1111 device probe, two-socket registration on supported boards, PCSR status changes, PCCR reset/power/float transitions, card-detect/BVD IRQ delivery, and clean linked-list removal.
