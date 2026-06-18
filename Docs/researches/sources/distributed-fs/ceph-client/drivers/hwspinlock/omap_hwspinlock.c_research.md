# sources/distributed-fs/ceph-client/drivers/hwspinlock/omap_hwspinlock.c

## Purpose
This provider driver registers TI OMAP/AM/K3 hardware spinlock blocks with the generic hwspinlock framework.

## Important APIs, Types, And Functions
- Register layout constants include `SYSSTATUS_OFFSET`, `LOCK_BASE_OFFSET`, and `SPINLOCK_NUMLOCKS_BIT_OFFSET`.
- `omap_hwspinlock_trylock()` acquires a lock by reading its register and checking for `SPINLOCK_NOTTAKEN`.
- `omap_hwspinlock_unlock()` releases by writing zero.
- `omap_hwspinlock_relax()` delays 50 ns while polling.
- `omap_hwspinlock_probe()` maps MMIO, enables runtime PM, determines lock count, initializes per-lock MMIO pointers, and registers the bank.

## Control Flow
Probe maps the resource, enables runtime PM, resumes the device to read `SYSSTATUS`, then puts it so runtime PM can gate the module when no locks are requested. The high SYSSTATUS bits encode a one-hot lock-bank count; the driver validates it and multiplies by 32 to get the number of locks. Each lock's `priv` points at its lock register. The provider is registered at base ID 0 during a `postcore_initcall`.

## State And Persistence
State consists of the hwspinlock bank and per-lock MMIO addresses. Runtime PM state is managed by the core while locks are requested. The hardware lock state lives in the SoC lock registers.

## Dependencies And Integration Points
The driver depends on platform MMIO resources, OF compatibles `ti,omap4-hwspinlock`, `ti,am64-hwspinlock`, `ti,am654-hwspinlock`, runtime PM, and the hwspinlock core.

## Risks
- The lock count decode accepts only one bit in the low nibble after shifting and `i <= 8`; wrong SYSSTATUS interpretation prevents probe.
- Base ID is fixed at 0 and only one block is supported.
- Read-to-lock semantics are hardware-specific and must not be "optimized" into ordinary status reads elsewhere.

## Test Signals
Validate probe on supported compatibles, SYSSTATUS lock-count variants, invalid count rejection, runtime PM transitions, trylock/unlock register semantics, relax callback use during timeout, and early boot registration ordering for board reservations.
