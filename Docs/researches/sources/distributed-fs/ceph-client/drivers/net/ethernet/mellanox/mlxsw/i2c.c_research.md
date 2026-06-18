# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/i2c.c

## Purpose
`i2c.c` implements the mlxsw bus backend for switch ASICs reachable over I2C. It discovers local command mailboxes, executes command-register transactions through chunked I2C transfers, optionally forwards platform IRQs into mlxsw core event handling, and registers/unregisters I2C clients as mlxsw core bus devices.

## Important APIs, Types, and Functions
- `struct mlxsw_i2c` stores command mailbox offsets/sizes, a command mutex, device/core/bus info, selected I2C block size, platform hotplug data, IRQ work, and IRQ number.
- Low-level helpers include `mlxsw_i2c_set_slave_addr()`, `mlxsw_i2c_wait_go_bit()`, `mlxsw_i2c_write_cmd()`, `mlxsw_i2c_write_init_cmd()`, and `mlxsw_i2c_get_mbox()`.
- Command execution flows through `mlxsw_i2c_cmd()`, `mlxsw_i2c_write()`, and the bus callback `mlxsw_i2c_cmd_exec()`.
- Bus lifecycle callbacks are `mlxsw_i2c_init()` / `mlxsw_i2c_fini()`. Driver lifecycle is `mlxsw_i2c_probe()`, `mlxsw_i2c_remove()`, `mlxsw_i2c_driver_register()`, and `mlxsw_i2c_driver_unregister()`.
- `mlxsw_i2c_irq_init()` optionally requests a shared falling-edge IRQ and schedules `mlxsw_core_irq_event_handlers_call()` from workqueue context.

## Control Flow
Probe allocates private state, derives a safe block size from adapter quirks, sends an immediate `QUERY_FW` command to validate access, waits for the GO bit to clear, reads mailbox offsets from the command interface region, fills bus info, initializes optional IRQ support, and registers with mlxsw core. Command execution serializes on `cmd.lock`. With an input mailbox, it computes register TLV size, writes the mailbox in block-sized I2C chunks, posts an ACCESS_REG command, waits for completion, and optionally reads output chunks. Without an input mailbox, it issues an initialization/query command and reads a default-sized output buffer.

## State and Persistence
Runtime state includes mailbox offsets/sizes discovered from hardware, block size, command mutex, IRQ work, bus info, and core pointer. Hardware state includes command interface GO/status bits and mailbox contents. The bus is marked `low_frequency`, influencing slower thermal polling elsewhere.

## Dependencies and Integration Points
The file depends on Linux I2C, optional `CONFIG_MLXREG_HOTPLUG`, mlxsw command helpers, core bus registration, and resource query helpers. It exposes no packet transport: `skb_transmit_busy()` always false and `skb_transmit()` returns success without sending, so users are command/environment-oriented drivers such as `minimal.c`.

## Risks
Retry loops use a timeout OR retry-count condition, which can continue while either bound remains true; changes here should preserve intended tolerance without indefinite waits. Mailbox size is derived from the input TLV and must remain aligned to u32. Adapter quirks smaller than the default block size reject the device. IRQ handler returns `IRQ_NONE` because it shares the line with another handler; platform integration must expect that.

## Test Signals
Test I2C adapters with and without quirks, insufficient max read/write lengths, mailbox discovery, command read/write with multi-block payloads, GO-bit timeout/status error, optional IRQ delivery, and removal cleanup. Minimal-driver module EEPROM reads are practical end-to-end command-path tests.
