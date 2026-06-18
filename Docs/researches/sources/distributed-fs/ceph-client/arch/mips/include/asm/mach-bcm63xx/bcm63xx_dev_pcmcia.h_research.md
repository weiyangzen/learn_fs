# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_pcmcia.h

**Purpose:** Defines platform data and registration for BCM63xx PCMCIA.

**Important APIs/types/functions:** Exports `struct bcm63xx_pcmcia_platform_data` with `ready_gpio`, and `bcm63xx_pcmcia_register()`.

**Control flow:** Board setup supplies the ready GPIO and calls registration, after which the PCMCIA driver uses fixed IO/memory windows and GPIO readiness to manage cards.

**State and persistence behavior:** No local state. Platform data persists in the registered device and references GPIO hardware state.

**Dependencies and integration points:** Integrates with BCM63xx IO window constants, chip-select setup, GPIO, IRQ tables, and PCMCIA core.

**Risks:** Wrong ready GPIO or unsupported SoC resources can make card detection unreliable. PCMCIA shares external bus windows with timing/chip-select setup.

**Test signals:** Probe PCMCIA on supported boards, validate ready GPIO polarity/state, card insertion/removal, IO/memory access windows, and unsupported-board absence.
