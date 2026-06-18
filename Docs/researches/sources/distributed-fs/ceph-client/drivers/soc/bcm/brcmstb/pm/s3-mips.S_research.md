# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/s3-mips.S

Purpose: low-level MIPS deep standby helper for Broadcom STB S3. It saves enough CPU state to survive power-down, triggers warm deep standby, and provides the `s3_reentry` resume label written into AON SRAM by C code.

Important APIs and symbols: exports `brcm_pm_do_s3(aon_ctrl_base, dcache_linesz)` and global `s3_reentry`. It uses global `gp_regs` from `pm-mips.c` to save return address, callee-saved registers, GP/SP/FP, and CP0 status.

Control flow: entry saves GPRs and CP0 status, writes back the `gp_regs` cacheline, programs `PM_WARM_CONFIG` then `PM_WARM_CONFIG | PM_PWR_DOWN`, enables CP0 interrupt 2, and waits. Resume jumps to `s3_reentry`, clears branch prediction structures, resets selected MMU registers, calls `plat_wired_tlb_setup`, restores saved GPRs and CP0 status, and returns to the C caller.

State and persistence: uses `gp_regs` as the cross-standby state carrier and relies on C code to preserve broader CP0 and MEMC state. AON PM control is the hardware persistence point for standby entry, while AON SRAM contains the reentry address.

Dependencies and integration: tightly coupled to `brcmstb_pm_s3()`, `pm.h`, BMIPS CP0 register semantics, `BMIPS_WARM_RESTART_VEC`, and `plat_wired_tlb_setup`. It assumes the saved register block is flushed before caches or memory become unavailable.

Risks and test signals: risks include incomplete register save set, cache writeback failure, wrong TLB defaults, and reentry address mismatch. Test signals are successful `PM_SUSPEND_MEM` wake, restored kernel execution context, stable TLB/cache behavior after wake, and no branch predictor or CP0 status related faults.
