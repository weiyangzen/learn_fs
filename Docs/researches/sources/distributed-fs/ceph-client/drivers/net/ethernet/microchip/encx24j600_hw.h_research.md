# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/encx24j600_hw.h

## Purpose
This header is the hardware contract for the ENCX24J600 family driver. It defines the SPI command opcodes, banked and unbanked SFR addresses, register bit masks, PHY registers, SRAM layout constants, receive-status-vector layout, and the regmap context shared by the main driver and regmap transport implementation.

## Important APIs, Types, and Functions
`struct encx24j600_context` stores the SPI device, normal register regmap, PHY regmap, regmap mutex, and currently selected register bank. The exported setup/API declarations are `devm_regmap_init_encx24j600`, `regmap_encx24j600_spi_write`, and `regmap_encx24j600_spi_read`. `struct rsv` describes the hardware RX status vector consumed by `encx24j600.c`: `next_packet`, `len`, and `rxstat`.

Key macro groups include single-byte commands like `SETETHRST`, `SETPKTDEC`, `SETTXRTS`, `ENABLERX`, `DISABLERX`, `SETEIE`, and `CLREIE`; register access commands like `RCR`, `WCR`, `BFS`, `BFC`, and raw buffer commands `RGPDATA`/`WGPDATA`/`RRXDATA`; banked register addresses such as `ETXST`, `ERXST`, `ERXTAIL`, `MACON1`, `MACON2`, `MAADR*`, and `EIE`; and bit definitions for `ESTAT`, `EIR`, `ECON1`, filters, MAC options, PHY status, and interrupt enables.

## Control Flow and State
The header itself has no executable control flow, but its layout dictates the driver sequence: select/register access via banked addresses, read/write PHY through a PHY regmap, split SRAM into TX and RX regions, and decode RX packets using `struct rsv` plus `RSV_GETBIT`. `RX_BUFFER_SIZE`, `SRAM_SIZE`, `ERXST_VAL`, `RXSTART_INIT`, and `RXEND_INIT` describe the receive ring region used by the runtime driver.

## Dependencies and Integration Points
It depends on Linux SPI, regmap, mutex, and device types being available through includers. The constants must match the external regmap implementation and the ENCX24J600 datasheet. The main driver depends on this header for all hardware register names and bit meanings.

## Risks
Many constants encode silicon-specific behavior; any mismatch corrupts packet memory or changes interrupt semantics. `MAX_FRAMELEN` is 1518 and used by the driver as a hard RX validation limit, so VLAN or jumbo frames are outside this implementation. Several defined constants are unused in the main driver, increasing the chance that future users assume untested coverage.

## Test Signals
Compile coverage validates macro availability. Runtime signals are successful reset using `EUDAST_TEST_VAL`, correct device ID extraction from `EIDLED`, stable RX cursor behavior around `RXSTART_INIT`/`RXEND_INIT`, and correct decode of RX error counters from `rxstat`.
