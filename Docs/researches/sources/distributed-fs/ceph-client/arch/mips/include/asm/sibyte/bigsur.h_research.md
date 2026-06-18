# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bigsur.h

Purpose: describes board-level constants for the BCM91x80A/B BigSur platform. It selects the board name and declares fixed generic-bus chip-select assignments and physical addresses for LEDs, IDE, and PCMCIA support.

Important APIs/types/functions: no functions or types are defined. Important symbols are `SIBYTE_BOARD_NAME`, `SIBYTE_HAVE_PCMCIA`, `SIBYTE_HAVE_IDE`, `LEDS_CS`, `LEDS_PHYS`, `IDE_CS`, `IDE_PHYS`, `K_GPIO_GB_IDE`, `K_INT_GB_IDE`, `PCMCIA_CS`, `PCMCIA_PHYS`, `K_GPIO_PC_READY`, and `K_INT_PC_READY`.

Control flow: the file is selected when `CONFIG_SIBYTE_BIGSUR` is enabled, usually through `board.h`. Feature macros gate whether IDE and PCMCIA definitions are visible. Interrupt constants are composed from GPIO lines and `K_INT_GPIO_0`, tying board wiring into the interrupt mapper.

State and persistence: there is no software state. The constants point to persistent board hardware mappings on the generic bus and GPIO interrupt lines.

Dependencies and integration: includes `sb1250.h` for common platform declarations and `bcm1480_int.h` for BCM1480 interrupt source numbering. It integrates with generic bus setup, IDE/PCMCIA platform devices, LED diagnostics, and board setup code.

Risks and test signals: hard-coded chip-select and physical address constants must match board strapping and generic-bus setup. Wrong GPIO-to-interrupt mapping breaks IDE/PCMCIA readiness signaling. Test signals are BigSur config build coverage, early LED writes, generic-bus resource registration, and interrupt delivery tests for IDE and PCMCIA ready GPIOs.
