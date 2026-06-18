# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_genbus.h

Purpose: defines generic bus, PCMCIA, and GPIO interrupt configuration bitfields for SiByte SoCs. It is used by board setup and platform device code to describe external chip-select timing, sizing, interrupt capture, drive strength, PCMCIA behavior, and GPIO interrupt mode.

Important APIs/types/functions: exported macro groups include `M_IO_*`/`V_IO_*` fields for generic-bus region configuration, size, start address, timing0/timing1, interrupt status/data/address/parity, and output drive registers; `M_PCMCIA_*` fields for configuration and card status; and `K_GPIO_INTR_*`, `V_GPIO_INTR_TYPE`, `G_GPIO_INTR_TYPE`, plus BCM1480 additional GPIO interrupt type fields.

Control flow: board code programs chip-select regions with bus width, multiplexing, timing, and caching attributes, then handles bus errors or external interrupts through status registers. PCMCIA setup uses config/status bits to control power/reset/card enable and detect card-ready/status. GPIO interrupt flow configures edge/level/high/low behavior and later routes GPIO lines into the interrupt mapper.

State and persistence: region config/timing/drive registers persist in hardware and define external device access behavior. Interrupt status registers expose latched event/error state. PCMCIA/GPIO status reflects board hardware inputs.

Dependencies and integration: depends on `sb1250_defs.h` for bit helpers and feature gates. It integrates with board headers such as `bigsur.h`, generic bus address macros in register headers, PCMCIA/IDE platform drivers, and interrupt mapper constants.

Risks and test signals: wrong timing or bus width can hang external bus cycles; wrong cacheability or address-base programming can corrupt device access. GPIO interrupt mode mismatches cause lost or stuck interrupts. Test signals include per-board resource setup builds, LED/IDE/PCMCIA access smoke tests, external bus error interrupt tests, and GPIO edge/level interrupt tests including BCM1480 additional type registers.
