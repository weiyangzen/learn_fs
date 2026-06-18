# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1xxx_psc.h

**Purpose:** Defines register layout and bit fields for Au1xxx Programmable Serial Controllers in AC97, I2S, SPI, and SMBus modes.

**Important APIs/types/functions:** Exports common select/control offsets and mode values, AC97 offsets and config/mask/status/event/CODEC/reset/GPIO bits, `psc_i2s_t` and I2S config/status/event masks, `psc_spi_t` and SPI config/mask/status/event/txrx bits, and SMBus config/mask/protocol/status/event/timer bits. Macros encode FIFO thresholds, DMA enable/disable, protocol start/stop, word lengths, clock divisors, baud fields, slot enables, and interrupt masks.

**Control flow:** PSC drivers select protocol mode, configure clock source/dividers/FIFO thresholds/word sizes, enable DMA or interrupt events, drive protocol control bits, and read status/event registers to service transfers. The header itself is declarative.

**State and persistence behavior:** No C storage. Consumers mutate PSC select/control and protocol registers; state persists until reset or mode switch. Reusing the same PSC across protocols makes mode state mutually exclusive.

**Dependencies and integration points:** Integrated by Alchemy SPI, SMBus/I2C, AC97, I2S/audio, and DBDMA drivers. Works with platform clock, pinmux, and DMA channel setup from other Au1x00 headers.

**Risks:** Many fields overlap by protocol and some macros perform arithmetic on caller-provided lengths/dividers without validation. Incorrect mode selection can make a shared PSC unavailable to another driver. Event/mask naming is similar but not identical between protocols.

**Test signals:** For each protocol, validate PSC select/control sequencing, transfer sizes and clock rates, FIFO thresholds, DMA and interrupt paths, underrun/overrun handling, and mode handoff/reset between users.
