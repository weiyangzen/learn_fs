# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPwrSeqCmd.c

## Purpose

`HalPwrSeqCmd.c` implements the Realtek hardware power-sequence command parser for RTL8723/RTL8188E-series devices. It interprets `struct wlan_pwr_cfg` arrays and performs register reads/writes, polling, delays, and termination. The file was read as a complete 145-line source.

## Important APIs, Types, and Functions

The only public function is `HalPwrSeqCmdParsing(struct adapter *padapter, u8 CutVersion, u8 FabVersion, u8 InterfaceType, struct wlan_pwr_cfg PwrSeqCmd[])`. It uses macros from `HalPwrSeqCmd.h`, including `GET_PWR_CFG_FAB_MASK`, `GET_PWR_CFG_CUT_MASK`, `GET_PWR_CFG_INTF_MASK`, `GET_PWR_CFG_CMD`, `GET_PWR_CFG_BASE`, `GET_PWR_CFG_OFFSET`, `GET_PWR_CFG_MASK`, and `GET_PWR_CFG_VALUE`.

## Control Flow

The parser loops over commands until `PWR_CMD_END`. It first filters each command by FAB, CUT, and interface masks. `PWR_CMD_WRITE` reads a byte from SDIO local or system register space, applies a mask/value update, and writes it back. `PWR_CMD_POLLING` repeatedly reads until the masked value matches the expected value or `pollingCount` exceeds 5000, delaying 10 microseconds between failed checks. `PWR_CMD_DELAY` delays in microseconds or milliseconds depending on the command value. `PWR_CMD_READ` is a no-op.

## State and Persistence Behavior

No file-local state is retained. Persistent effects are direct writes to SDIO local registers or system registers, and time spent polling/delaying during power transitions.

## Dependencies and Integration Points

It includes `<drv_types.h>` and `<HalPwrSeqCmd.h>`, and integrates with adapter register IO through `SdioLocalCmd52Read1Byte`, `SdioLocalCmd52Write1Byte`, `rtw_read8`, `rtw_write8`, `udelay`, and generated power sequence arrays.

## Risks and Edge Cases

The loop trusts the command array to contain `PWR_CMD_END`; malformed arrays can run indefinitely through memory. `pollingCount` is not reset per polling command, so multiple polling commands share the 5000 count budget. Millisecond delays are implemented as `udelay(offset * 1000)`, which can busy-wait for long delays. `PWR_CMD_READ` does nothing, so read commands only serve as placeholders unless callers expect side effects elsewhere.

## Test Signals

Unit tests with synthetic power arrays, timeout tests for polling mismatch, SDIO versus normal register write tests, command-filter tests for cut/fab/interface masks, and suspend/resume or power-on hardware traces are useful signals.
