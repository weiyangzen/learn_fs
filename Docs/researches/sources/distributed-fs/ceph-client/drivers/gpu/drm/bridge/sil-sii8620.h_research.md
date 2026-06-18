# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/sil-sii8620.h

## Purpose

`sil-sii8620.h` is the private register map for `sil-sii8620.c`. It defines the paged register addresses, bit masks, field masks, and composed values needed to program the SiI8620 transmitter. It has no functions, structs, or storage; its contract is exact hardware ABI naming for the C driver.

## Important APIs, Types, And Macros

The public surface is C preprocessor constants. Major groups are system identity/control (`REG_VND_ID*`, `REG_DEV_ID*`, `REG_SYS_CTRL1`, `REG_DPD`, `REG_PWD_SRST`), fast interrupt routing (`REG_FAST_INTR_STAT` and `BIT_FAST_INTR_STAT_*`), HPD/GPIO/TMDS/DDC controls, TDM/HSIC/eMSC controls, TMDS receiver and packet filter registers, EDID/devcap FIFO controls, MHL datapath/PLL/CBUS/CoC/DoC analog controls, HDCP2.x registers, MHL3 HDMI-to-MHL controls, TPI input/output/infoframe/system-control registers, MHL devcap/status/scratchpad base registers, MDT Gen2 write-burst controls, CBUS MSC command/status/interrupt registers, and discovery controls/status bits for RGND, MHL1/2, MHL3, and disconnect events.

Convenience composed values include `VAL_M3_CTRL_MHL1_2_VALUE`, `VAL_M3_CTRL_MHL3_VALUE`, `VAL_TPI_FORMAT(_fmt, _qr)`, `VAL_DISC_CTRL4()`, MHL PLL clock ratio values, CBUS drive/RGND values, TX zone values, and `VAL_CBUS_MHL_DISCON`.

## Control Flow

The header has no runtime control flow. Its macros drive control flow in `sil-sii8620.c`: `REG_FAST_INTR_STAT` bits select IRQ subhandlers, `REG_CBUS_DISC_INTR0` bits control discovery and disconnect paths, `REG_CBUS_INT_0` bits drive MSC receive/transmit handling, `REG_INTR9` and `REG_INTR3` bits complete devcap/EDID/DDC operations, and MHL/TPI/DP/PLL registers are programmed during disconnect, discovery, eCBUS transition, and video start.

## State And Persistence Behavior

No software state is stored here. The named registers represent volatile hardware state, sticky interrupt bits cleared by writeback, FIFO ports, MHL peer-visible capability/status memory, DDC/EDID buffers, power/reset state, and analog/link training controls. Persistence behavior is entirely hardware-defined and managed by `sil-sii8620.c`.

## Dependencies And Integration Points

The header assumes Linux `BIT()` is available through including C files. It is tightly coupled to the `sii8620_i2c_page[]` mapping in the C file: register high bytes select I2C page indices, so a register address and page table must stay synchronized. It also relies on MHL constants from DRM bridge MHL headers for array offsets and protocol values used beside these register definitions.

## Risks

Incorrect register addresses or masks can misroute interrupts, break DDC/EDID, corrupt MHL capability/status exchange, or damage discovery/link training sequences. Several fields are analog tuning or vendor-derived magic values, so accidental refactoring is high risk. Naming is not generated in a standard `REG_FIELD` style, so compile-time validation is limited to direct macro references.

## Test Signals

Static signals are successful build of `sil-sii8620.c` and absence of undefined macros. Runtime signals include correct chip ID reads, expected interrupt demux, successful MHL discovery, devcap/xdevcap reads, EDID FIFO operation, eMSC burst activity, SCDT video start, and stable MHL1/MHL3 mode validation across packed and normal pixel modes.
