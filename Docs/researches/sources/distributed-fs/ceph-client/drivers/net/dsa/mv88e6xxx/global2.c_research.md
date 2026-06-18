# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global2.c

Purpose: implements Global 2 register operations for management frame routing, device/trunk/PVT tables, ingress-rate initialization, switch MAC, ATU statistics, priority override, EEPROM, SMI PHY proxying, watchdog handling, miscellaneous port-width mode, and nested interrupt domains.

Important APIs/types/functions: base accessors are `mv88e6xxx_g2_read/write/wait_bit()`. Exported helpers include management reserved-to-CPU setup, trunk/device/PVT table writes, EEPROM 8/16-bit get/set, Clause 22/45 SMI PHY accessors, watchdog ops structures, `mv88e6xxx_g2_irq_setup/free()`, MDIO IRQ mapping, and ATU stats get/set.

Control flow: command-style blocks wait for busy bits, write data/address registers, issue command words, then wait/read result registers. IRQ setup creates a 16-entry domain, maps nested interrupts, requests the Global1 device IRQ, and wires watchdog handling as a nested IRQ.

State and persistence: switch management/trunk/PVT/priority/EEPROM settings live in hardware. EEPROM content is persistent. Runtime state includes `chip->g2_irq`, `device_irq`, `watchdog_irq`, and MDIO bus IRQ assignments.

Dependencies/integration: used by devlink resources/PVT, PHY/MDIO code, watchdog ops tables, DSA multi-chip routing, ethtool EEPROM hooks, and Global1 device interrupt signaling.

Risks: EEPROM writes can persistently alter board configuration and 16-bit writes require write-enable. Watchdog action on newer chips may reset the switch. IRQ setup error unwind must dispose mappings consistently; watchdog request failure currently returns without disposing `watchdog_irq`.

Test signals: MDIO Clause 22/45 PHY reads, ethtool EEPROM odd/even offsets, PVT devlink dumps, trunk setup/clear, nested PHY/watchdog IRQs, watchdog reset recovery, and teardown after partial setup failures.
