# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/sw.h

## Purpose
Declares shared RTL8192DE global spinlocks for dual-MAC power, firmware download, and power/efuse coordination.

## Important APIs, Types, And Functions
Exports `globalmutex_power`, `globalmutex_for_fwdownload`, and `globalmutex_for_power_and_efuse` as `spinlock_t` objects. Their definitions are in `sw.c`.

## Control Flow
The header has no executable flow. Callers include it to serialize critical low-level register operations across MAC instances.

## State And Persistence
The locks themselves are persistent module globals. They protect shared hardware state such as MAC power-on/off markers and other dual-MAC register operations.

## Dependencies And Integration Points
Requires Linux spinlock declarations via included users. `phy.c` uses `globalmutex_power` around dual-MAC power-on/off checks. Other RTL8192DE files may use the firmware and efuse locks.

## Risks
Global locks create cross-device coupling for devices handled by the same module. Any caller must use IRQ-safe locking consistently and avoid long register polling while holding the lock.

## Test Signals
Lockdep under dual-MAC bring-up, concurrent interface power transitions, firmware download, and efuse access is the primary validation signal.
