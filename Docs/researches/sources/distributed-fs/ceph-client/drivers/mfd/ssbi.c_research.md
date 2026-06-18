# sources/distributed-fs/ceph-client/drivers/mfd/ssbi.c

## Purpose
`ssbi.c` implements the Qualcomm Single-wire Serial Bus Interface parent driver. It provides serialized byte read/write helpers over SSBI, SSBI2, or PMIC-arbiter controller variants and populates child devices.

## Important APIs, Types, and Functions
`struct ssbi` stores mapped registers, a spinlock, controller type, and selected read/write operations. Public exports are `ssbi_read()` and `ssbi_write()`. Controller helpers include `ssbi_wait_mask()`, `ssbi_read_bytes()`, `ssbi_write_bytes()`, `ssbi_pa_transfer()`, `ssbi_pa_read_bytes()`, and `ssbi_pa_write_bytes()`.

## Control Flow
Probe maps the controller registers, reads `qcom,controller-type`, selects either the SSBI/SSBI2 or PMIC-arbiter accessors, initializes the lock, and populates child OF devices. Public read/write APIs take the spinlock, call the selected accessor, and release the lock.

## State and Persistence
State is per-controller runtime state plus volatile MMIO registers. SSBI2 writes high address bits through `SSBI2_MODE2`. No suspend cache or persistent storage is present.

## Dependencies and Integration Points
It depends on platform MMIO resources, OF, `linux/ssbi.h`, and downstream SSBI child drivers that call the exported read/write helpers with the parent `struct device`.

## Risks and Edge Cases
Transactions busy-wait up to `SSBI_TIMEOUT_US`; slow or stuck hardware returns `-ETIMEDOUT`. PMIC-arbiter transfers can return `-EPERM` on transaction denied. The controller type property is required and invalid values fail probe. SSBI2 address-high programming is shared state protected by the lock.

## Test Signals
Validate all three controller types, concurrent child read/write serialization, timeout paths, PMIC-arbiter denied transactions, multi-byte operations, and child OF population.
