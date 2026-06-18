# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pow-defs.h

## Purpose
`cvmx-pow-defs.h` is the generated CSR definition file for Octeon POW, the Packet Order/Work scheduler, plus SSO-compatible work-queue interrupt aliases. It defines hardware registers for group masks, QoS thresholds and randomization, input queue counts and interrupts, work queue interrupts, no-schedule counters, ECC and BIST status, performance counters, reset masks, and per-core work-schedule accounting.

## Important APIs, Types, And Functions
Primary macros include `CVMX_POW_PP_GRP_MSKX`, `CVMX_POW_QOS_THRX`, `CVMX_POW_QOS_RNDX`, `CVMX_POW_WQ_INT`, `CVMX_POW_WQ_INT_THRX`, `CVMX_POW_WQ_INT_CNTX`, `CVMX_POW_IQ_CNTX`, `CVMX_POW_IQ_THRX`, `CVMX_POW_IQ_INT`, `CVMX_POW_IQ_INT_EN`, `CVMX_POW_ECC_ERR`, `CVMX_POW_BIST_STAT`, `CVMX_POW_NOS_CNT`, `CVMX_POW_NW_TIM`, `CVMX_POW_PF_RST_MSK`, and performance counter macros for work add, work schedule, tag switch, deschedule, and combined counters. SSO aliases include `CVMX_SSO_WQ_INT`, `CVMX_SSO_WQ_IQ_DIS`, `CVMX_SSO_WQ_INT_PC`, `CVMX_SSO_PPX_GRP_MSK`, and `CVMX_SSO_WQ_INT_THRX`.

Important unions include `cvmx_pow_pp_grp_mskx` for per-processor group masks and QoS priorities; `cvmx_pow_qos_thrx` for min/max/free/buffer/deschedule thresholds; `cvmx_pow_qos_rndx` for QoS randomization; `cvmx_pow_wq_int*` for interrupt summary, thresholds, pending counts, and IQ disable bits; `cvmx_pow_ecc_err` for single/double-bit ECC, syndrome, remote pointer, and illegal operation reporting; and `cvmx_pow_bist_stat` for multiple internal RAM/CAM self-test fields.

## Control Flow
There are no functions. External POW code programs group masks for each core, sets QoS threshold/randomization policy, configures work queue and input queue interrupt thresholds, monitors counters, and handles ECC or BIST status. Interrupt flow is external: read summary, inspect count/threshold registers, then clear or mask according to hardware semantics.

## State And Persistence
POW state is hardware scheduling state. Group masks and QoS priorities decide which cores can receive which work groups. Thresholds and randomization influence scheduler admission and fairness. Interrupt registers persist pending state. ECC status persists hardware error latches. Performance counters accumulate scheduler events until reset or cleared by external mechanisms.

## Dependencies And Integration Points
The header depends on CSR address infrastructure and endian bitfields. It integrates with `cvmx-pow.h` operation helpers, `cvmx-wqe.h` work queue entries, PIP-generated group/QoS/tag metadata, PKO atomic-tag locking, and interrupt controllers that route POW/SSO work-queue interrupts to cores.

## Risks
Misconfigured group masks can make work unreachable or send it to unintended cores. Threshold mistakes can cause interrupt storms or delayed scheduling. ECC fields are hardware-fault indicators and may require precise clear/recovery sequences not visible in the type definitions. Indexed macros mask core, QoS, and group offsets, so invalid inputs can silently target valid slots. SSO aliases share the same broad hardware region but not necessarily identical semantics on every Octeon generation.

## Test Signals
Test signals include group-mask scheduling tests, QoS threshold and randomization fairness tests, WQ/IQ interrupt threshold trigger and mask behavior, no-schedule counter changes under disabled groups, performance counter increments for add/schedule/deschedule/tag-switch paths, ECC injection or error-latch handling, BIST validation after reset, and cross-block tests confirming PIP-assigned groups and PKO atomic tags interact correctly with POW scheduling.
