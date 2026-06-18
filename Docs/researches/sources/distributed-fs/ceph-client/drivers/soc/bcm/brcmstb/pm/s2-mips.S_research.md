# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/s2-mips.S

Purpose: low-level MIPS assembly standby implementation for Broadcom STB S2. It executes with careful cache and interrupt handling while the CPU and PLLs enter and leave standby.

Important APIs and symbols: exports `LEAF(brcm_pm_do_s2)`, taking a `u32` parameter array with AON control base, DDR PHY base, timer base, I-cache line size, restart vector address, and restart vector size. It uses PM and timer constants from `pm.h`.

Control flow: the function saves callee-saved registers, loads arguments, locks its own code and the warm restart vector into I-cache, writes `PM_S2_COMMAND` to AON PM control, enables CP0 interrupt 2, waits, polls DDR PHY PLL status, delays roughly 1 ms with TIMER1, signals power-back-up through `AON_CTRL_HOST_MISC_CMDS`, clears PM control, unlocks I-cache lines, restores CP0 status and saved registers, then returns 0.

State and persistence: saves only CPU registers and CP0 status on the stack. Hardware state is changed in AON PM control, host misc command, DDR PHY polling, and timer registers. I-cache lock/unlock is transient but critical while memory/power state is unstable.

Dependencies and integration: called by `brcmstb_pm_s2()` after C code redirects vectors and prepares hardware. Depends on BMIPS CP0 interrupt behavior, valid KSEG/MMIO addresses in 32-bit arguments, and the warm restart vector being present.

Risks and test signals: risks include incorrect cache line size, bad restart vector length, missed PLL-ready polling, and timer frequency assumptions in the fixed delay. Test signals are repeated S2 standby/resume cycles, interrupt wake behavior, cache coherency after return, and absence of hangs in PLL polling or timer wait loops.
