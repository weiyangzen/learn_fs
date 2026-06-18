# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_i2s.h

Purpose: Register definition header for the base Rockchip I2S controller driver and its machine-driver users.

Important APIs, types, and functions: Defines bitfields for TXCR/RXCR format, channel select, word width, CKR master/slave and clock dividers, FIFO level, DMA control, interrupts, transfer start/stop, clear logic, TX/RX data registers, divider ids, channel constants, register offsets, and IO direction GRF encodings.

Control flow: No executable code. The macros are consumed by `rockchip_i2s.c` to build regmap updates and by machine drivers for shared divider identifiers.

State and persistence: No state. Macro values map directly to hardware register layout and therefore must remain consistent with SoC manuals.

Dependencies and integration: Requires Linux `BIT` and standard kernel integer macros from including translation units. Integrates with regmap access tables and GRF writes in the I2S driver.

Risks and edge cases: Incorrect shifts or masks can corrupt adjacent hardware fields. The IO direction values differ from the TDM header, so cross-using base I2S and I2S/TDM macros would be unsafe. Comments include typos but not behavioral issues.

Test signals: Build coverage plus runtime audio format/channel tests are the main validation. Register dumps during 2/4/6/8-channel playback should match expected CSR and GRF direction fields.
