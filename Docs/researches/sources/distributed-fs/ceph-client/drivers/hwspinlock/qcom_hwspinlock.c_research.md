# sources/distributed-fs/ceph-client/drivers/hwspinlock/qcom_hwspinlock.c

## Purpose
This provider driver exposes Qualcomm hardware mutex blocks as 32 generic hwspinlocks. It supports both syscon-backed regmaps and direct MMIO regmaps for several Qualcomm mutex layouts.

## Important APIs, Types, And Functions
- `struct qcom_hwspinlock_of_data` describes offset, stride, and optional MMIO regmap configuration.
- `qcom_hwspinlock_trylock()` writes the APPS processor owner ID and reads back the owner to confirm acquisition.
- `qcom_hwspinlock_unlock()` verifies ownership and writes zero.
- `qcom_hwspinlock_bust()` clears a lock only when the current owner matches a caller-provided ID.
- `qcom_hwspinlock_probe_syscon()` parses a `syscon` phandle plus offset/stride cells.
- `qcom_hwspinlock_probe_mmio()` maps MMIO and creates a regmap from match data.
- `qcom_hwspinlock_probe()` allocates regmap fields for all 32 locks and registers the bank.

## Control Flow
Probe first tries the syscon path; if the phandle is absent it falls back to direct MMIO using compatible-specific offset/stride/config. For each lock it creates a full 32-bit `regmap_field` at `base + i * stride` and stores it in `lock[i].priv`. The provider registers 32 locks at base ID 0 during `postcore_initcall`.

## State And Persistence
The bank stores per-lock `regmap_field` handles. Hardware ownership is encoded as a processor ID in each mutex register. The driver uses APPS processor ID 1 for acquisition and release.

## Dependencies And Integration Points
It depends on platform devices, OF match data, syscon/regmap, optional MMIO resources, `MFD_SYSCON` from Kconfig, and the hwspinlock core.

## Risks
- Ownership ID is hard-coded to `QCOM_MUTEX_APPS_PROC_ID`; platforms with different APPS IDs would fail or mis-own locks.
- Unlock logs an error if not owner but still writes zero, which can clear another owner's lock.
- Syscon property parsing requires offset and stride in cells 1 and 2; malformed bindings fail probe.
- Base ID 0 and fixed 32-lock count assume one mutex bank instance.

## Test Signals
Validate syscon and MMIO probe paths, all compatible offset/stride values, regmap field allocation failures, trylock ownership readback, unlock when owned/not owned, bust matching and non-matching owner IDs, duplicate provider registration behavior, and postcore registration timing.
