# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_regs.h

Purpose: generated main TPC configuration register map for `DCORE0_TPC0_CFG`. It exports 103 `mmDCORE0_TPC0_CFG_*` address constants from `0x400BC18` through `0x400BDFC`.

Important APIs/types/functions: no executable API. Register families cover TPC identity/count, stall and clock controls, input-queue rate limiting, TSB MTRR and masks, lock registers, CGU controls, floating point rounding/bias, dcache and scoreboard controls, arbitration weights, LUT base addresses, semaphores/flags, status, base address translation, command/execute/stall, icache base, read/write rate limits, interrupt cause/mask, work-queue credits, opcode execution, and inflight/occupancy counters.

Control flow: none internally. External driver code sequences writes to configuration, command, and execute registers, then polls status/interrupt fields using masks from `dcore0_tpc0_cfg_masks.h`.

State and persistence behavior: this is the core TPC control MMIO state. Writes can change execution readiness, cache/clock behavior, protection attributes, interrupt delivery, and kernel launch behavior until reset or explicit reprogramming.

Dependencies and integration points: included by `gaudi2_regs.h`; masks are in `dcore0_tpc0_cfg_masks.h`. `gaudi2_masks.h` uses related status masks to define idle checks, and `gaudi2_security.c` relies on generated register ranges and selected register allowlists.

Risks: this header spans control, status, and interrupt surfaces. Wrong addresses can stall engines, mask interrupts, misprogram lookup-table bases, or corrupt command execution. Some names contain generated spelling quirks such as `ADDERESS` and `OCCOUPY`; downstream code must use the generated spelling exactly.

Test signals: full driver compile, TPC reset/idle tests, interrupt mask/cause tests, command launch smoke tests, generated address comparison, and security policy checks for privileged control registers.
