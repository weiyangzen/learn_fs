# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc4_qm_regs.h

## Purpose

This generated header defines the Gaudi TPC4 QMAN register offsets. It supplies symbolic `mmTPC4_QM_*` constants for queue-manager global control, producer/completion queues, command processors, arbitration, clock/rate limiting, indirect gateway, and error registers. It contains 406 macros from `mmTPC4_QM_GLBL_CFG0` at `0xF08000` through `mmTPC4_QM_GLBL_MEM_INIT_BUSY` at `0xF08D00`.

## Important APIs, types, and macros

The header exports compile-time register constants only. Key macro families are:

- `GLBL_*`: global config/protection/error config, secure and non-secure property registers, status registers, message enables, AXCACHE, global error address/write-data capture, and memory-init busy state.
- `PQ_*`: four producer queues with base low/high, size, producer index, consumer index, queue config, ARUSER, and status registers.
- `CQ_*`: five completion/command queues with config, ARUSER, status, pointer low/high, transfer size, control, latched pointer/size/control status, and input FIFO counters.
- `CP_*`: five command-processor lanes with message base address windows, LDMA offsets, fence read data and counters, processor status, current instruction address, barrier config, debug, and ARUSER/AWUSER properties.
- `ARB_*`: arbitration config, WRR weights, 32 master available-credit registers, 32 choice-push offsets, slave/master controls, message security properties, arbiter base, state/status, error cause/message enable/drop status, and 32 master credit status registers.
- `CGM_*`, `LOCAL_RANGE_*`, `CSMR_STRICT_PRIO_CFG`, HBW/LBW rate-limit registers, and `IND_GW_APB_*` indirect gateway registers.

## Control flow and state behavior

The file has no functions or branches. Driver control flow uses these constants in register writes and address calculations. Observed users stop TPC4 command processors by writing `mmTPC4_QM_GLBL_CFG1`, map queue IDs `GAUDI_QUEUE_ID_TPC_4_0..3` to `mmTPC4_QM_PQ_PI_0..3` doorbells, prepare non-secure property registers for MMU ASID handling, and construct protection masks from TPC4 QMAN offsets. Queue state lives in device registers and in DMA-visible queue memory addressed by these registers; persistence is hardware-reset scoped.

## Dependencies and integration points

The header is included by `include/gaudi/asic_reg/gaudi_regs.h`; block-level base constants live in `gaudi_blocks.h`, where `mmTPC4_QM_BASE` is `0x7FFCF08000ull`. Higher-level queue identity is connected to Gaudi queue IDs and async events such as `GAUDI_EVENT_TPC4_QM`. Field definitions are shared with peer QMANs, for example TPC0 QMAN bit shifts used when writing equivalent TPC4 registers.

## Risks and test signals

The risk is address fidelity. `PQ_PI_*` offsets are doorbells, so a wrong mapping can submit work to the wrong queue or fail to wake hardware. Security-sensitive global property and ARUSER/AWUSER registers participate in ASID and protection-bit setup. Test signals include successful Gaudi compilation, queue submission tests covering TPC4 lanes, reset/shutdown paths that stop TPC QMAN CPs, MMU context-switch tests, and security tests that verify protected QMAN register windows.
