# sources/distributed-fs/ceph-client/drivers/net/can/m_can/tcan4x5x-core.c

## Purpose
`tcan4x5x-core.c` is the SPI peripheral wrapper for Texas Instruments TCAN4x5x M_CAN controllers. It handles TCAN-specific registers, reset/wake GPIOs, regulators, device identification, interrupt clearing, mode changes, and supplies regmap-backed M_CAN operations to the common class driver.

## Important APIs, Types, And Functions
- TCAN device, configuration, interrupt, MCAN, MRAM, mode, wake, and watchdog registers are defined as `TCAN4X5X_*`.
- `struct tcan4x5x_version_info` describes detected device variants and pin capabilities.
- `tcan4x5x_read_reg()`, `tcan4x5x_write_reg()`, `tcan4x5x_read_fifo()`, and `tcan4x5x_write_fifo()` implement M_CAN transport over regmap.
- `tcan4x5x_init()` clears TCAN interrupts, enables TCAN interrupt sources, unmasks error status, selects normal mode, and applies optional NWKRQ voltage behavior.
- `tcan4x5x_deinit()` puts the transceiver into standby mode.
- `tcan4x5x_get_gpios()`, `tcan4x5x_check_gpios()`, and `tcan4x5x_find_version()` handle reset/wake/state pins and device identity.
- `tcan4x5x_can_probe()` is the SPI probe path; `tcan4x5x_can_remove()` unregisters and powers down the device.

## Control Flow
Probe allocates an M_CAN class device, checks that the parsed MRAM layout fits within the TCAN MRAM window, gets the optional `vsup` regulator, obtains or defaults the CAN clock, validates the 20 to 40 MHz frequency range, configures SPI, initializes regmap, powers the chip, resets it through GPIO or software reset, detects the TCAN variant, disables absent wake/state pins in hardware, reads DT options, clears and disables interrupts, enables wakeup if requested, and calls `m_can_class_register()`.

During common M_CAN open/start, the `.init` callback wakes the device if needed, clears TCAN interrupt/status registers, enables TCAN-level interrupt bits that include the MCAN interrupt, clears error mask status, selects normal mode, and optionally sets `TCAN4X5X_NWKRQ_VOLTAGE_VIO`. On stop/deinit, the device returns to standby.

Suspend and resume wrap the common M_CAN PM helpers and enable or disable IRQ wake when the device is a wake source.

## State And Persistence
TCAN-specific state is in `struct tcan4x5x_priv`: regmap, SPI device, reset/wake/state GPIOs, regulator, aligned regmap TX/RX buffers, and the `nwkrq_voltage_vio` flag. Common CAN state lives in the embedded `m_can_classdev`. Hardware mode, interrupt masks, wake pin behavior, and MRAM are volatile device state.

## Dependencies And Integration Points
The file depends on SPI, regmap, GPIO descriptors, regulators, clocks, device-tree properties, and exported M_CAN class APIs. It also depends on `tcan4x5x_regmap_init()` from `tcan4x5x-regmap.c` and `struct tcan4x5x_priv` from `tcan4x5x.h`.

## Risks And Edge Cases
- If no clock is provided, the driver logs an error but defaults to 40 MHz; board descriptions must match actual hardware timing.
- Wake/state GPIO absence is handled differently depending on detected variant capabilities; generic fallback assumes both pins exist.
- The SPI IRQ must be valid for interrupt-driven operation; common peripheral code relies on threaded IRQ and RX offload.
- Regulator power is disabled on probe failure and remove, but runtime open/close power cycling is not used.
- `tcan4x5x_read_reg()` ignores the regmap read return code and returns whatever `val` holds if the read fails.

## Test Signals
Test TCAN4552, TCAN4553, and generic-compatible devices; reset GPIO and software reset paths; missing wake/state GPIO handling; optional regulator; clock absent, low, high, and valid cases; wakeup-source suspend/resume; SPI half/full duplex controllers; CAN FD TX/RX; and TCAN bus fault interrupt clearing.
