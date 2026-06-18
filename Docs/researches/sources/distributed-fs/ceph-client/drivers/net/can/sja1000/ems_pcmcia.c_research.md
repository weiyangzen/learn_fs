# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/ems_pcmcia.c

Purpose: this PCMCIA adapter driver supports EMS CPC-CARD devices with up to two SJA1000 channels. It configures the PCMCIA socket, maps the card memory window, detects channels, registers them with the SJA1000 core, and supplies a custom shared interrupt demultiplexer.

Important types and APIs: `struct ems_pcmcia_card` stores channel count, the PCMCIA device, per-channel netdevs, and mapped base address. Register accessors are byte MMIO helpers. `ems_pcmcia_interrupt()` loops over registered channels and calls `sja1000_interrupt()` until no channel handles more work. Probe/remove entry points are `ems_pcmcia_probe()` and `ems_pcmcia_remove()`.

Control flow: PCMCIA probe configures IO resources and an attribute/common memory window, maps the selected page, enables the device, then calls `ems_pcmcia_add_card()`. The card add path allocates card state, maps 4 KiB of card memory, verifies the `0xAA55` signature, resets and maps CAN controllers, allocates up to two SJA1000 netdevs, probes PeliCAN mode, assigns clock/OCR/CDR, marks `SJA1000_CUSTOM_IRQ_HANDLER`, registers channels, and finally requests the shared IRQ for the card-level demux handler. Remove frees IRQ, unregisters/free channels, unmaps controllers, sends unmap command, frees state, and disables PCMCIA.

State and persistence: card state and channel netdevs are in memory. Hardware state includes mapping/reset commands written to card base and SJA1000 mode/CDR/OCR registers. No data persists across unplug/reload.

Dependencies and integration points: depends on PCMCIA core, memory window mapping, SocketCAN SJA1000 common APIs, and shared IRQ support. It relies on the card signature to avoid calling SJA1000 handlers after card removal.

Risks and test signals: `ems_pcmcia_probe()` logs some setup errors but returns 0 in those branches, which can hide probe failure from the bus core. `ems_pcmcia_del_card()` unconditionally calls `free_irq()`, so partial failure before request_irq needs careful validation. Tests should cover card insertion/removal, one- and two-channel cards, IRQ demux under high load, signature loss during ISR, and failed PCMCIA resource setup.
