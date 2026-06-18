# sources/distributed-fs/ceph-client/drivers/hwspinlock/sun6i_hwspinlock.c

## Purpose
This provider driver registers Allwinner sun6i-compatible hardware spinlock blocks with the generic hwspinlock framework. It also exposes a debugfs file reporting the detected lock count when debugfs is enabled.

## Important APIs, Types, And Functions
- `struct sun6i_hwspinlock_data` stores the bank pointer, reset control, AHB clock, debugfs dentry, and detected lock count.
- `sun6i_hwspinlock_trylock()` acquires by reading the lock register and checking for zero.
- `sun6i_hwspinlock_unlock()` releases by writing zero.
- `sun6i_hwspinlock_debugfs_init()` creates `sun6i_hwspinlock/supported` under debugfs when configured.
- `sun6i_hwspinlock_probe()` handles reset/clock setup, decodes lock count from `SYSSTATUS`, initializes per-lock MMIO addresses, registers cleanup, and registers the bank.

## Control Flow
Probe maps MMIO resource 0, allocates private data, gets the `ahb` clock and reset, deasserts reset, enables the clock, decodes `num_banks` from bits 28 and above of `SYSSTATUS`, maps values 1..4 to 32..256 locks, allocates a flexible bank for that count, fills lock register addresses, initializes debugfs, installs a cleanup action, sets drvdata, and registers the bank with base ID 0.

## State And Persistence
State includes clock/reset enablement, debugfs entry, dynamic lock count, and lock MMIO pointers. Cleanup removes debugfs, disables the clock, and asserts reset. Hardware lock state is volatile in the lock registers.

## Dependencies And Integration Points
It depends on platform MMIO resources, OF compatible `allwinner,sun6i-a31-hwspinlock`, reset controls, AHB clock, optional debugfs, and the hwspinlock core.

## Risks
- Lock count decoding works around inconsistent datasheets; future SoCs may encode unsupported values.
- No `relax()` callback is provided, so timeout loops use only the core's retry behavior.
- Debugfs creation failure is non-fatal and normalized to NULL, so diagnostics may silently be absent.
- Fixed base ID 0 assumes a single bank per SoC.

## Test Signals
Validate reset/clock sequencing, SYSSTATUS decode for 32/64/128/256 locks and invalid values, debugfs supported count, devm cleanup on each failure point, trylock/unlock semantics, and registration with dynamic lock counts.
