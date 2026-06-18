# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic0_qm0_masks.h

## Purpose

`nic0_qm0_masks.h` is an auto-generated bitfield definition header for the Gaudi NIC0 QM0 QMAN block. Unlike the `_regs.h` files, it does not define addresses; it defines 534 `NIC0_QM0_*_SHIFT` and `NIC0_QM0_*_MASK` macros that describe how to pack and unpack fields inside NIC QMAN registers. It is the bit-layout companion to `nic0_qm0_regs.h`, and the driver also reuses the same masks with other NIC QMAN instances when their register layout is identical.

## Important APIs, types, and functions

There are no functions or types. The macro groups cover the common QMAN bitfields:

- Global enable, stop, flush, protection, error, status, and message-enable fields for PQF, CQF, CP, and arbiter units.
- Secure and non-secure properties with ASID and MMBP fields for five property slots.
- PQ/CQ base, size, PI/CI, credit, inflight, busy, IFIFO, pointer, transfer-size, and control fields.
- CP message base, LDMA offset, fence data/count, status, current-instruction, barrier, debug, ARUSER, and AWUSER fields.
- Arbiter configuration, choice queue, WRR weight, master/slave credit, message AWUSER/security properties, state, fullness, error, and credit status fields.
- Clock-gating (`CGM_*`), local range, strict priority, HBW/LBW rate limiting, AXCACHE, indirect APB gateway, global error address/data, and memory-init busy fields.

The driver consumes these masks through `FIELD_PREP()` and direct mask tests, most visibly in `gaudi_masks.h` for `NIC_QMAN_ENABLE`, `NIC_QMAN_GLBL_ERR_CFG_MSG_EN_MASK`, and `NIC_QMAN_GLBL_ERR_CFG_STOP_ON_ERR_EN_MASK`.

## Control flow

The header has no control flow. It affects control flow by determining the values written to address macros from `nic0_qm0_regs.h` and related NIC QMAN register headers. For example, `gaudi_init_nic_qman()` writes `NIC_QMAN_ENABLE` to `mmNIC0_QM0_GLBL_CFG0 + nic_offset`, and that composite value is built from `NIC0_QM0_GLBL_CFG0_PQF_EN_MASK`, `CQF_EN_MASK`, and `CP_EN_MASK`. Stop/flush and error handling paths similarly depend on these bit definitions to affect the intended QMAN subunits.

## State and persistence behavior

The macros are compile-time constants only. The state they describe lives in hardware registers: enable bits, stop/flush requests, protection settings, queue credits, pointer values, command processor fences, arbiter credits, rate limiter state, and captured error data. Incorrect masks can persistently program wrong fields even when the address is correct, causing queues to stay disabled, errors not to generate messages, or idle/power-gating status to be misread.

## Dependencies and integration points

`gaudi_regs.h` includes this header after the Gaudi NIC QMAN register address headers. `gaudi_masks.h` depends on it for reusable NIC QMAN composite values. `gaudi.c` writes NIC QMAN global config/error/protection registers and reads status registers whose interpretation depends on these masks. The same bit layout is reused with `mmNIC0_QM1_*` addresses and with offset-derived NIC instances, so this single mask header is broader than only NIC0 QM0.

## Risks

Mask errors are as dangerous as address errors: a wrong shift or mask can enable the wrong queue fetcher, fail to stop a command processor, corrupt ASID/MMBP protection, misconfigure queue credits, or hide arbiter errors. Several fields use all 32 bits, while others are narrow status/control fields; consumers must not assume uniform widths. Because NIC0 QM1 uses the same masks but different addresses, maintainers must distinguish bit-layout sharing from address sharing.

## Test signals

Build tests should cover `FIELD_PREP()` uses for every referenced mask. Runtime tests should initialize NIC QMANs, submit work on all NIC streams, exercise stop/flush/error paths, verify RAZWI/error IRQ routing, read idle status through `GLBL_STS0` and `CGM_STS`, and validate ASID programming for NIC QMAN non-secure properties. Static tests can compare mask families against the corresponding register families and verify expected field widths for enable, stop, error, and status composites.
