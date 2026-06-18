# sources/distributed-fs/ceph-client/drivers/mfd/rz-mtu3.c

### Purpose
`rz-mtu3.c` is the MFD parent and shared register-access layer for the Renesas RZ/G2L MTU3a multi-function timer. It maps timer MMIO, controls reset and clock references, initializes per-channel metadata, exports register read/write/start/stop helpers for child drivers, and creates counter and PWM children.

### Important APIs, Types, And Functions
Exported APIs include `rz_mtu3_shared_reg_read/write/update_bit()`, `rz_mtu3_8bit_ch_read/write()`, `rz_mtu3_16bit_ch_read/write()`, `rz_mtu3_32bit_ch_read/write()`, `rz_mtu3_is_enabled()`, `rz_mtu3_enable()`, and `rz_mtu3_disable()`. Static helpers map channel/register enum offsets to physical MMIO offsets and compute timer start-register offsets and bit positions. `struct rz_mtu3_priv` stores `mmio`, reset control, and a spinlock.

### Control Flow
Probe allocates public and private state, maps MMIO resource 0, gets an exclusive reset control and clock, deasserts reset, initializes the spinlock and nine channel locks/metadata entries, and adds `rz-mtu3-counter` and `pwm-rz-mtu3` children. A device-managed cleanup action removes children and asserts reset. Exported channel read/write helpers look up the channel-specific offset table and issue `readb/readw/readl` or `writeb/writew/writel`. Start/stop and shared bit-update paths lock around shared registers, modify the correct bit, and write back.

### State, Persistence, And Dependencies
Runtime state is MMIO mapping, reset state, clock handle, shared spinlock, per-channel locks, busy flags, and child devices. Hardware persistence is all MTU3 register programming by children and start/stop bits in shared timer start registers. Dependencies include platform device resources, reset, clock, MFD core, spinlocks, bit operations, MMIO accessors, and public `linux/mfd/rz-mtu3.h` definitions.

### Integration Points
The counter and PWM child drivers use exported helpers and `struct rz_mtu3_channel` objects from parent drvdata. The parent abstracts nonuniform channel register layouts: channel 8 lacks 16-bit registers, only channels 1 and 8 have 32-bit register tables, and shared start registers differ by channel group.

### Risks
Offset arrays are indexed by enum offsets from the public header; a mismatch between public enum values and private array dimensions would yield wrong MMIO addresses. Some helpers return zero or do nothing for unsupported channel widths instead of failing, which can hide misuse by children. Shared register updates are protected by a spinlock, but raw channel register access is not globally serialized. Cleanup asserts reset only through the devm action after child removal; failures before action registration must assert reset through the error path.

### Test Signals
Tests should validate probe/reset sequencing, child creation, and cleanup reset assertion. Register-access tests should sample every channel's 8-bit offsets, valid 16-bit channels, valid 32-bit channels 1 and 8, and unsupported-width behavior. PWM/counter integration tests should verify start/stop bits for channel groups 0-4/8, 5, and 6-7, plus concurrent shared register bit updates under interrupt-disabled spinlock.
