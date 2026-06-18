# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-amdpsp.c

## Purpose
AMD PSP arbitration support for DesignWare I2C buses shared with the Platform Security Processor. It installs lock operations and internal acquire/release hooks so x86 asks PSP for temporary bus ownership before I2C activity.

## Important APIs, Types, And Functions
`enum psp_i2c_req_type` and `struct psp_i2c_req` model PSP acquire/release commands. Global state includes `psp_i2c_access_mutex`, `psp_i2c_sem_acquired`, `psp_i2c_access_count`, `psp_i2c_mbox_fail`, `psp_i2c_dev`, and `_psp_send_i2c_req`. Key functions are `psp_send_i2c_req()`, `psp_acquire_i2c_bus()`, `psp_release_i2c_bus()`, and `i2c_dw_amdpsp_probe_lock_support()`.

## Control Flow
Probe support checks CCP reachability, DesignWare `ARBITRATION_SEMAPHORE`, singleton binding, root PCI device ID to choose Cezanne platform mailbox versus doorbell, PSP platform access readiness, then installs adapter `lock_ops` and DesignWare internal lock callbacks. Acquire increments access count, skips PSP if mailbox failed or reservation remains valid, otherwise polls PSP acquire. Release decrements access count and either leaves reservation for delayed work or sends release when the reservation window elapsed.

## State And Persistence
Arbitration state is process-global, not per-controller, enforcing one bound bus. Reservation time is tracked in jiffies and released by delayed work after `PSP_I2C_RESERVATION_TIME_MS` when no users remain. Mailbox failure permanently degrades to host-exclusive behavior for the module lifetime.

## Dependencies And Integration Points
Depends on AMD PSP/CCP platform access APIs, PCI root-device detection, workqueues, mutexes, DesignWare platform probing, and I2C adapter lock operations.

## Risks
The singleton global design rejects additional PSP-managed buses. `trylock_bus()` appears to return immediately when `rt_mutex_trylock()` succeeds, so its PSP acquire path warrants scrutiny against lock API expectations. PSP communication failure intentionally falls back to success, which preserves host function but risks real PSP contention. Doorbell/mailbox status interpretation is hardware-specific.

## Test Signals
Test `-EPROBE_DEFER` when PSP is unavailable, Cezanne versus doorbell selection, nested lock/unlock count behavior, delayed release after idle, mailbox failure fallback, duplicate instance rejection, and transfers that span write-wait-read sequences under adapter lock.
