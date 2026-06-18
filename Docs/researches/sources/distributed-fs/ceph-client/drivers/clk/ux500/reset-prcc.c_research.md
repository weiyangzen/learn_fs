<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/reset-prcc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/reset-prcc.c

## Purpose

`reset-prcc.c` exposes U8500 PRCC reset lines through the Linux reset-controller framework. It maps each PRCC cluster's soft-reset registers and translates two-cell DT reset specifiers into flattened reset IDs.

## Important APIs, Types, And Functions

`PRCC_RESET_LINE(prcc_num, bit)` flattens cluster and bit. `prcc_num_to_index()` maps PRCC numbers 1/2/3/5/6 to array indices. `u8500_prcc_reset_base()` finds the MMIO base. Reset ops implement pulse reset, assert, deassert, and status using `PRCC_K_SOFTRST_CLEAR`, `PRCC_K_SOFTRST_SET`, and `PRCC_K_RST_STATUS`. `u8500_prcc_reset_xlate()` validates two-cell specifiers.

## Control Flow

`u8500_prcc_reset_init()` maps all physical bases provided by `u8500_of_clk.c`, fills `reset_controller_dev`, and registers it. Runtime reset calls compute base and bit from the ID, then write active-low reset controls; pulse reset holds reset for one microsecond before releasing it.

## State And Persistence Behavior

Reset state persists in PRCC hardware. The controller object stores mapped bases and the reset framework device. There is no unregister or unmap path because it is early built-in U8500 infrastructure.

## Dependencies And Integration Points

It depends on Linux reset-controller APIs, raw MMIO, DT phandle translation, and `prcc.h` numbering. It is registered from the `prcc-reset-controller` child under the U8500 clock node.

## Risks And Test Signals

There is no null-base guard after failed `ioremap()`, and `u8500_prcc_reset_base()` does not reject invalid bits above 31. Test valid/invalid DT specifiers, reset pulse timing, active-low status semantics, and reset of representative UART/I2C/SD/MMC peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/reset-prcc.c -->
