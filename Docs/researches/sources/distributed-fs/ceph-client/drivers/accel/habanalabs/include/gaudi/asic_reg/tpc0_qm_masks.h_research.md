# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc0_qm_masks.h

## Purpose

`tpc0_qm_masks.h` is an auto-generated bitfield header for the Gaudi TPC0 queue manager (`TPC0_QM`, prototype `QMAN`). It exports `TPC0_QM_*_{SHIFT,MASK}` macros used to encode and decode queue-manager MMIO registers. The file contains no functions, types, or executable code; its public interface is the generated macro set.

The queue manager controls producer queues, completion queues, command processors, arbitration, error handling, security properties, rate limiting, clock gating, indirect APB access, and error capture for the TPC0 command path. It is paired with `tpc0_qm_regs.h`, which supplies the `mmTPC0_QM_*` addresses.

## Important APIs, Types, And Macros

Global configuration fields include `GLBL_CFG0` enables for four producer queues (`PQF_EN`), five completion queues (`CQF_EN`), and five command processors (`CP_EN`). `GLBL_CFG1` contains stop and flush fields for the same queue families. `GLBL_PROT` exposes protection fields for PQF, CQF, CP, error, and arbitration paths. `GLBL_ERR_CFG` controls error message enable and stop-on-error behavior for queue families and arbitration.

Security and MMU integration is represented by secure and non-secure property fields for five channels, each carrying a 10-bit `ASID` and an `MMBP` bit. Global status fields expose idle/stop state, read/command/message/write/fence errors, and per-channel message-enable fields. Channel 4 has specialized `GLBL_STS1_4` and `GLBL_MSG_EN_4` naming while sharing most CP/CQ error fields with other channels.

Producer queue fields cover base low/high, size, producer index, consumer index, credit and inflight limits, ARUSER bits, credit/free counts, inflight counts, empty state, and busy state. Completion queue fields mirror credit and inflight controls and add completion queue pointer low/high, target size, control/report fields, status copies of pointer/size/control, and internal FIFO count.

Command processor fields include message base address pairs for four message base regions across five CP channels, LDMA size/source/destination offset fields, four fence read-data increment values, four fence counters, CP status bits (`MSG_INFLIGHT_CNT`, ready bits, software stop, fence id, fence in-progress), current instruction low/high, barrier guard settings, debug state/stall bits, and CP ARUSER/AWUSER upper bits.

Arbitration fields include arbiter type/master/enable/mask/no-stall controls, choice queue push/head values, weighted round-robin weights, clear, master available credits, credit increment and choice offsets, slave enable/quiet/watchdog/id, message max-inflight and AWUSER/security properties, base addresses, state/fullness/message status, error cause/message-enable/drop status, and master credit status. The file uses the generated misspelling `CHOISE` in several macro names.

Power and system integration fields include clock-gating manager thresholds and status (`CGM_CFG`, `CGM_STS`, `CGM_CFG1`), local range base/size, CSMR strict-priority type, HBW/LBW rate-limit token/saturation/timeout/enable fields, global AXCACHE AR/AW fields, indirect gateway APB command/address/write/read/status fields, global error address/write-data capture fields, and memory-initialization busy bits.

## Control Flow And State

There is no local control flow. These masks describe how driver code controls hardware queue-manager state. Writes to enable, stop, flush, credit, pointer, security, rate-limit, and arbitration fields change queue-manager behavior until reset or later writes. Reads from status, counter, error, debug, and busy fields observe hardware progress and failure state.

Gaudi driver initialization programs PQ base/size/index registers, LDMA offsets, error handling, arbitration watchdogs, protection bits, CP message bases, and `GLBL_CFG0` enables. Command submission writes producer queue producer-index doorbells. Reset and stop paths write `GLBL_CFG1` stop bits. Error handling reads `GLBL_STS1_*`, `ARB_ERR_CAUSE`, CP status, and fence information. Power-management paths program or disable clock-gating manager fields.

## Dependencies And Integration Points

The header has only an include guard dependency but is semantically coupled to `tpc0_qm_regs.h` and the Gaudi QMAN driver code. It is used with Linux bitfield helpers and HabanaLabs register access helpers for field writes and reads.

TPC0 masks are reused with offsets for other TPC queue managers. `gaudiP.h` defines `TPC_QMAN_OFFSET` from TPC instance register bases, and `gaudi.c` adds offsets to TPC0 `mmTPC0_QM_*` addresses while using TPC0 bit layouts. This means TPC0 mask correctness affects all TPC queue-manager instances.

Important integration points include command queue initialization, doorbell selection for four TPC PQ streams, MMU ASID preparation through `GLBL_NON_SECURE_PROPS_*`, queue error reporting, completion queue pointer mapping, CP fence monitoring, clock-gating control, and security/protection-bit setup.

## Risks And Edge Cases

The largest risk is field/address mismatch with the hardware database. Queue manager registers often combine multiple queue-family bitmaps in one word, so an incorrect mask can enable, stop, flush, or stop-on-error the wrong queue. Security fields are particularly sensitive: wrong ASID/MMBP or AXUSER values can route DMA under the wrong address space or protection domain.

Several generated spellings, especially `CHOISE`, are part of the macro ABI and should not be normalized by hand. Some channel-specific fields omit producer-queue bits for channel 4, so generic code must respect per-register variants instead of assuming all status registers share identical fields.

Credit, inflight, fence, and counter fields are bounded by masks but not by semantic checks in this header. Driver code must avoid programming invalid queue sizes, overflowing producer indices, enabling queues before bases are valid, clearing errors before diagnostic capture, or interpreting transient busy/idle fields without appropriate polling rules.

The indirect APB gateway has command, ready, and error bits; callers need ordering and timeout logic not represented here. Clock-gating and rate-limit fields can degrade or stall queue progress if programmed incorrectly.

## Test Signals

Compile-time tests should catch missing macro references in Gaudi code. Generator validation should verify that related fields do not overlap and that channel variants match the hardware spec.

Runtime signals include successful TPC queue initialization, correct producer-index doorbell behavior for all four PQs, completion queue pointer/status mapping, CP message-base and fence handling, expected stop/flush behavior during reset, accurate ASID programming, usable arbitration under load, no unexpected `GLBL_STS1` or `ARB_ERR_CAUSE` bits during normal workloads, and clock-gating/rate-limit settings that do not introduce hangs.
