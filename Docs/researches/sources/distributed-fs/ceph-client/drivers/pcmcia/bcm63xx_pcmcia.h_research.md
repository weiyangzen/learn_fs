# sources/distributed-fs/ceph-client/drivers/pcmcia/bcm63xx_pcmcia.h

Purpose: Defines the private data model for the BCM63xx PCMCIA socket driver, including card-type bits and the per-socket state structure used by `bcm63xx_pcmcia.c`.

Important APIs and types: Defines `BCM63XX_PCMCIA_POLL_RATE`, card masks `CARD_CARDBUS`, `CARD_PCCARD`, `CARD_5V`, `CARD_3V`, `CARD_XV`, and `CARD_YV`, and `struct bcm63xx_pcmcia_socket`.

Control flow: No executable logic. The structure fields determine how the implementation tracks resources, mappings, polling, and socket state between callbacks.

State and persistence: `struct bcm63xx_pcmcia_socket` stores the embedded `pcmcia_socket`, platform data, spinlock, register and memory resources, mapped I/O base, detected card type, old status for change reporting, requested socket state, and polling timer.

Dependencies and integration points: Includes PCMCIA socket-service types and BCM63xx platform data. It is private to the BCM63xx socket implementation and must track the source file's register/mapping assumptions.

Risks: Field ownership is split between timer context, socket callbacks, and probe/remove; lock coverage must stay consistent. Card-type flags are electrical interpretations, so changing values requires auditing the status-reporting logic.

Test signals: Compile coverage with `CONFIG_PCMCIA_BCM63XX`, timer/status callback execution, and lockdep or race testing around insertion/removal validate the header contract.
