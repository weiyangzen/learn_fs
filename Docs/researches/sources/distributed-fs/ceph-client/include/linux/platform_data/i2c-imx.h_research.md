
# sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-imx.h

## Purpose
This header defines platform data for the Freescale/NXP i.MX I2C driver.

## Important APIs And Types
`struct imxi2c_platform_data` contains a single `bitrate` field, measured in Hz.

## Control Flow, State, And Persistence
There is no executable flow. The i.MX I2C driver reads `bitrate` at probe or setup time and programs controller clock dividers accordingly. Runtime state is I2C controller configuration and active transfers.

## Dependencies And Integration Points
It integrates i.MX board/platform data with the Linux I2C controller driver and clock framework.

## Risks And Test Signals
Risks include unsupported bitrate values, incorrect parent clock assumptions, and transfer failures at too-high speeds. Test signals include bus frequency measurement, standard/fast-mode device transfers, arbitration/NAK handling, and probe behavior when bitrate is zero or unspecified.
