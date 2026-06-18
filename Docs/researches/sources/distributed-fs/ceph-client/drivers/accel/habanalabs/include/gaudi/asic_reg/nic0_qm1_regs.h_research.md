# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic0_qm1_regs.h

## Purpose

`nic0_qm1_regs.h` is the auto-generated register address map for the Gaudi NIC0 QM1 QMAN instance. It exports 406 `mmNIC0_QM1_*` constants from `mmNIC0_QM1_GLBL_CFG0` at `0xCE2000` through `mmNIC0_QM1_GLBL_MEM_INIT_BUSY` at `0xCE2D00`. Its normalized QMAN layout matches `nic0_qm0_regs.h`, but it names the second QMAN engine for NIC0's paired NIC-port arrangement.

## Important APIs, types, and functions

There are no functions or C types. The register families mirror NIC0 QM0:

- Global configuration, protection, secure/non-secure properties, status, message-enable, error, AXCACHE, and memory-init registers.
- Four producer queue register groups and five completion queue register groups.
- Command processor message-base, LDMA, fence, status, current-instruction, barrier, debug, ARUSER, and AWUSER registers.
- Arbiter configuration, WRR, credit, choice queue, message property, state, error, and credit-status registers.
- Clock gating, local range, strict priority, rate limiting, and indirect APB gateway registers.

Bitfield interpretation is provided by `nic0_qm0_masks.h` because the two NIC0 QMAN instances share the same field layout.

## Control flow

The header has no executable control flow. It participates in runtime control flow through address selection. `gaudi_init_nic_qmans()` uses the delta `mmNIC0_QM1_GLBL_CFG0 - mmNIC0_QM0_GLBL_CFG0` to move between paired NIC QMAN instances as it walks NIC ports. Doorbell selection maps `GAUDI_QUEUE_ID_NIC_1_0` through `_1_3` to `mmNIC0_QM1_PQ_PI_0 + q_off` after checking `HW_CAP_NIC1`. Engine-idle/debug paths read `mmNIC0_QM1_GLBL_STS0 + offset` and `mmNIC0_QM1_CGM_STS + offset` for odd-numbered NIC ports.

## State and persistence behavior

The macros persist only in the compiled driver. The named hardware state includes QM1 queue bases, producer/consumer indices, CP message bases, LDMA offsets, fence counters, arbiter state, global error routing, protection bits, and enable/stop state. That state remains active until hardware reset, port disablement, or reconfiguration. Because the driver often uses QM0 masks with QM1 addresses, address and mask consistency are both required for correct persistent hardware configuration.

## Dependencies and integration points

`gaudi_regs.h` includes this file. `gaudiP.h` uses base deltas involving QM1 to define NIC engine offsets. `gaudi.c` uses QM1 addresses for NIC1 queue doorbells, MMU non-secure property preparation when `HW_CAP_NIC1` is set, idle checks for odd ports, and offset progression across NIC pairs. It is structurally paired with `nic0_qm0_regs.h` and uses `nic0_qm0_masks.h` for bit fields.

## Risks

The main risk is mismatched arithmetic between QM0 and QM1. If the QM1 base or layout drifts, loops that derive offsets for paired NIC ports will program wrong register banks. Since masks are not namespaced for QM1, maintainers might incorrectly expect a separate `NIC0_QM1_*_MASK` header; using QM0 masks is intentional only while the layouts remain identical. Doorbell errors in this file directly affect user-visible NIC queue progress.

## Test signals

Tests should cover enabled NIC1/odd-port initialization, queue submissions on all four QM1 streams, producer-index doorbells for `GAUDI_QUEUE_ID_NIC_1_*`, MMU ASID programming of `mmNIC0_QM1_GLBL_NON_SECURE_PROPS_*`, QMAN idle/debug reads, and stop/disable paths. Static tests should compare normalized QM1 names to QM0 names and verify the expected `0x2000` base delta between `0xCE0000` and `0xCE2000`.
