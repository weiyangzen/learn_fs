# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qxp-rsrc.c

## Purpose
Defines the sorted SCU resource allowlist for i.MX8QXP clocks.

## Important APIs, Types, And Functions
The file contains `imx8qxp_clk_scu_rsrc_table[]` and exported `imx_clk_scu_rsrc_imx8qxp`. The table is passed as match data for `fsl,imx8qxp-clk`.

## Control Flow
There is no executable logic. The SCU core validates requested resource IDs with `bsearch()` before allocating SCU clock devices.

## State And Persistence Behavior
State is immutable compiled data. It is not persisted or modified. The array order is part of the functional contract because search assumes ascending values.

## Dependencies And Integration Points
Depends on `rsrc.h` firmware constants and `clk-scu.h`. It gates registration for the higher-level i.MX8QXP clock tree in `clk-imx8qxp.c`.

## Risks
Incorrect entries cause false missing clocks or invalid SCFW requests. The table differs from i.MX8QM and i.MX8DXL, so using the wrong compatible data can hide or expose the wrong resources.

## Test Signals
Boot on i.MX8QXP, validate expected UART/I2C/SPI/PWM/USDHC/ENET/display/audio clocks register, and confirm invalid resources are skipped without SCFW errors.
