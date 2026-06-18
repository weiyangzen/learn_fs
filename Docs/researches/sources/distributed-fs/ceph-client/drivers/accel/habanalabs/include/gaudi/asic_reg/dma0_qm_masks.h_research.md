# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma0_qm_masks.h

## Purpose

`dma0_qm_masks.h` is the auto-generated bit-field map for the Gaudi DMA0 queue-manager block. It defines how to enable, stop, flush, protect, monitor, and debug primary queue fetchers, completion queue fetchers, command processors, the QMAN arbiter, clock-gating logic, APB indirect gateway, and related error paths.

## Important APIs, Types, and Constants

Global QMAN fields include `DMA0_QM_GLBL_CFG0_*` enable bits for PQF, CQF, and CP units; `GLBL_CFG1_*` stop/flush bits; `GLBL_PROT_*`; `GLBL_ERR_CFG_*`; secure and non-secure ASID/MMBP properties per stream; `GLBL_STS0` idle/stop indicators; `GLBL_STS1` and `GLBL_MSG_EN` error/status bits for fetch and CP failures.

Queue fields describe PQ base, size, PI, CI, credit/inflight status, CQ base/size/control/status, and CQ internal FIFO counts. CP fields cover message base addresses, LDMA source/destination/size offsets, fence read-data and counters, CP status, current instruction address, barrier guard config, debug state, and CP ARUSER/AWUSER attributes. Arbiter fields cover arbitration type, master/slave enable, WRR weights, credit counters, message limits, error causes, watchdogs, and status. Later groups cover clock gating, local ranges, strict priority, HBW/LBW rate limiting, AXCACHE, indirect APB gateway, global error capture, and memory-init busy state.

## Control Flow

The header has no code flow. Gaudi initialization applies these fields when configuring each DMA QMAN. Queue setup writes PQ base/size/PI/CI, CP LDMA offsets, CP message base registers, and barrier config. Per-QMAN setup writes global error config, error-message address/data, arbiter error-message enable, watchdog timeout, global protection, stop/flush reset, and finally global enable masks. Stop/reset paths use `GLBL_CFG1_CP_STOP` masks, and clock-gating paths use CGM registers.

## State and Persistence Behavior

The masks describe persistent QMAN configuration and live queue state. PQ/CQ base and size registers persist while queues are active; PI/CI and status registers change as commands flow. CP fence counters and current-instruction registers expose live execution state. Error and arbiter status fields persist until cleared by the appropriate driver or hardware flow. Security property fields define how QMAN-generated AXI transactions are tagged.

## Dependencies and Integration Points

This file pairs with `dma0_qm_regs.h` and with the common queue ABI in `qman_if.h`. It is reused for multiple DMA QMANs by adding `DMA_QMAN_OFFSET`. It also integrates with synchronization manager registers through CP message-base programming, with DMA core registers through LDMA offset fields, and with interrupt routing through global and arbiter error-message fields.

## Risks

Queue-manager bit fields are concurrency- and security-sensitive. Wrong enable/stop/flush masks can leave engines running during reset or disabled during submission. Wrong PQ/CQ or CP message semantics can corrupt host queues, lose completions, or generate interrupts to the wrong target. Secure/non-secure ASID/MMBP fields and protection bits affect address translation and isolation. Arbiter watchdog and credit fields can create starvation or deadlocks if misprogrammed.

## Test Signals

Signals include successful QMAN initialization across all DMA channels, working command submission and completion for every stream, correct CP fence behavior, correct stop/flush during reset, no unexpected QMAN global/arbiter errors under stress, and expected error-message interrupts for RAZWI or malformed commands. Queue wraparound and multi-stream arbitration stress tests are especially valuable.
