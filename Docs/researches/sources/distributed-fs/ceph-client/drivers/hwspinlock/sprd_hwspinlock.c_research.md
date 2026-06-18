# sources/distributed-fs/ceph-client/drivers/hwspinlock/sprd_hwspinlock.c

## Purpose
This provider driver registers Spreadtrum hardware spinlock blocks with 32 token registers and optional user/master ID recording.

## Important APIs, Types, And Functions
- `struct sprd_hwspinlock_dev` contains MMIO base, enable clock, and embedded `hwspinlock_device`.
- `sprd_hwspinlock_trylock()` reads the token register; zero means acquired. On failure it reads the master/user ID register and logs the owner.
- `sprd_hwspinlock_unlock()` writes the magic not-taken value `0x55aa10c5`.
- `sprd_hwspinlock_relax()` delays 10 ns while polling.
- `sprd_hwspinlock_probe()` maps MMIO, enables the clock, enables user ID recording, initializes token addresses, and registers 32 locks.

## Control Flow
Probe requires an OF node, allocates the provider structure with room for 32 locks, maps the register block, gets and enables the `enable` clock, registers a devm cleanup action, writes `HWSPINLOCK_USER_BITS` to `RECCTRL`, stores each token register address in `lock->priv`, sets drvdata, and registers the bank at base ID 0.

## State And Persistence
Runtime state is the enabled clock, MMIO base, and bank. The hardware records ownership information when configured. The cleanup action disables the clock on driver detach or probe failure.

## Dependencies And Integration Points
It depends on OF platform probing, an `enable` clock, MMIO resources, devm actions, and the hwspinlock core. Compatible string is `sprd,hwspinlock-r3p0`.

## Risks
- Failure logging in `trylock()` can be noisy because every unsuccessful poll may emit a warning with owner ID.
- Base ID and lock count are fixed, limiting multi-bank support.
- The hardware-specific token semantics are non-obvious: read zero for success and write a magic value for unlock.

## Test Signals
Validate clock acquisition/cleanup, RECCTRL write, token address mapping, trylock success/failure owner reporting, unlock magic write, timeout polling with relax, OF-only probe rejection, and devm unwind on registration failure.
