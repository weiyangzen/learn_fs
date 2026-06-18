# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sun6i-p2wi.c

Purpose: implements Allwinner SUN6I Push-Pull Two Wire Interface as an I2C/SMBus-style adapter for the AXP221-style PMIC bus. P2WI is not normal SMBus: it supports one target, byte-data transactions, parity bits, and no per-byte ACK.

Important APIs/types/functions: `struct p2wi` contains the adapter, completion, last interrupt status, MMIO base, clock, reset control, and optional fixed target address. `p2wi_smbus_xfer()` is the only transfer hook and supports `I2C_FUNC_SMBUS_BYTE_DATA`. `p2wi_interrupt()` stores/clears status and completes transfers. Probe/remove handle clock/reset/register setup and adapter registration.

Control flow: probe validates requested clock frequency, ensures no more than one child node, optionally captures the target `reg`, maps registers, obtains IRQ/clock/reset, deasserts reset, installs the IRQ, soft-resets the block, programs divider and SDA delay, and registers the adapter. A transfer checks the fixed target address if configured, writes command/data registers, programs read/write data length, ensures no active transfer bit is set, enables interrupts, starts hardware, waits for completion, checks load-busy and transfer-error flags, and returns read data for reads.

State and persistence: persistent state includes target address, clock/reset resources, and register configuration. Per-transfer state is the completion and `status` captured by the IRQ. Remove asserts reset and unregisters the adapter.

Dependencies and integration: depends on OF compatible `allwinner,sun6i-a31-p2wi`, reset and clock frameworks, platform IRQ/MMIO, and I2C core SMBus transfer callbacks. It can be used without a child node for userspace `i2c-dev`, disabling address filtering.

Risks: `wait_for_completion()` has no timeout, so a lost interrupt or wedged controller can hang callers. Protocol support is intentionally narrow and incompatible with normal SMBus devices. Clock divider clamping may silently run at a different rate than requested. Only one child target is supported by design.

Test signals: probe with zero/too-high clock, multiple child nodes, no-child user-space mode, address mismatch, byte read/write success, load-busy and transfer-error interrupt statuses, reset assertion on remove, and interrupt-loss fault injection.
