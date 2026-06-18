<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubpi.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubpi.h

Purpose: Defines SN0 hub Processor Interface register offsets and bitfields for CPU protection, CPU enable/NMI/reset, interrupt pending/masks, cross-call interrupts, realtime/profiling timers, graphics controls, error stacks/status, BIST, SYSAD checking, and NACK counters.

Important APIs/types/functions: `PI_*` register offsets for protection, CPU presence/enable, interrupt masks, CC pending set/clear, realtime/profiling counters, BIST, graphics, and error registers; CALIAS constants; error masks `PI_ERR_*`; composed fatal/misc error masks; error status/stack field masks; `ERR_STACK_SIZE_BYTES`; C formats `pi_err_stack_t`, `pi_err_stat0_t`, `pi_err_stat1_t`; `rtc_time_t`; and SYSAD/interrupt-pending/NACK constants.

Control flow: Low-level SN code programs CPU and IO protection, enables CPUs, sends NMIs or soft resets, sets/clears interrupt and cross-call pending bits, configures realtime/profiling interrupts, records processor-interface errors into stack/status registers, and reads or clears those errors during machine-check style recovery.

State and persistence: State is entirely hardware-visible: per-CPU pending/mask registers, CPU present/enable bits, realtime compare/pending/enables, graphics credit/page controls, error-stack base/size, error status words, CRB timeout state, SYSAD checking enables, and NACK counters.

Dependencies and integration points: Depends on Linux integer types and is included by `hub.h`, SN interrupt code, NMI/error handling, realtime clock code, and SMP cross-call/IPI paths. Address access is supplied by hub address macros from includers.

Risks: Many registers are per-slice with A/B offsets, so wrong offset arithmetic targets the wrong CPU. Error-status fields use different shifts for stack versus status registers. Duplicate `ERR_STK_ADDR_SHFT` is a legacy artifact; changes here can break assembly/error decode code.

Test signals: SN CPU interrupt/IPI tests, realtime timer/profiler interrupts, NMI and soft-reset paths, PI error injection/decoding, and SYSAD error-check build/runtime coverage are useful signals.

Source read size: 409 lines, 15947 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubpi.h -->
