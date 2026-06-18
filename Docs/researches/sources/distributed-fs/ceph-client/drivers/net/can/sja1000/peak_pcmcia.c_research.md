# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/peak_pcmcia.c

Purpose: this PCMCIA driver supports PEAK-System PCAN-PC Card adapters with one or two SJA1000 channels, including card-level power control and LED activity indication.

Important types and APIs: `struct pcan_pccard` stores the PCMCIA device, channel array, cached common-control register, firmware version, mapped IO window, and LED timer. Per-channel state tracks netdev and previous RX/TX byte counts. The driver provides SJA1000 read/write callbacks, a custom ISR `pcan_isr()`, channel discovery/cleanup helpers, EEPROM write helpers for connector power, and PCMCIA probe/remove.

Control flow: probe negotiates PCMCIA IO config, enables the device, allocates card state, maps IO ports into an iomem-like window, reads firmware version, detects/registers channels, sets up the LED timer, requests the shared IRQ, and powers CAN connectors through EEPROM. `pcan_add_channels()` initializes common CCR reset/LED bits, releases channel reset, allocates each SJA1000 netdev, checks PeliCAN mode presence, assigns callbacks/clock/OCR/CDR, disables CLKOUT on secondary channels, marks custom IRQ handling, and registers the device. The ISR checks card presence and calls `sja1000_interrupt()` for each channel up to a bounded loop count. LED timer changes LED state based on interface up state and RX/TX byte counter deltas.

State and persistence: runtime state includes cached CCR, firmware version for presence checks, channel netdevs, and timer state. The EEPROM write used by `pcan_set_can_power()` may persist connector power configuration on the card, so unlike most files this driver writes device nonvolatile memory. Driver memory state is freed on removal.

Dependencies and integration points: depends on PCMCIA core, IO port mapping, timers, SJA1000 core, shared IRQs, and card EEPROM/SPI registers. It maps ioport resources through `ioport_map()` because the SJA1000 core expects iomem-style accessors.

Risks and test signals: EEPROM power writes include busy-wait loops with schedule and bounded retry; failures leave power state uncertain. Hot-unplug during ISR is handled by firmware-version presence checks. Tests should cover one/two-channel cards, firmware detection, connector power on/off, LED timer transitions, card removal during interrupt, SPI busy timeouts, and no-channel probe failure.
