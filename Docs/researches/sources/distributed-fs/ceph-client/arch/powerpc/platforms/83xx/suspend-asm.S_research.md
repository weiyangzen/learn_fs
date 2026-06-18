# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/suspend-asm.S

## Purpose
`suspend-asm.S` implements the low-level MPC83xx deep-sleep transition and resume path used by the PMC suspend driver.

## Important APIs, Types, and Functions
The exported entry `mpc83xx_enter_deep_sleep(phys_addr_t immrbase)` saves the first RAM words, CPU HID/debug/MMU/timebase/general register state into `mpc83xx_sleep_save_area`, writes the bootloader resume magic and physical `mpc83xx_deep_resume` address, disables MMU paths, maps current/default IMMR with BATs, moves IMMR back to the reset location, configures flash mapping, sets sleep mode and `MSR_POW`, then resumes by restoring RAM words, CPU state, BATs, segment registers, timebase, and registers before `rfi`.

## Control Flow, State, and Persistence
Static data holds the save area and IMMR base. The routine intentionally modifies low RAM words as a firmware contract and later restores them.

## Dependencies and Integration Points
It depends on `suspend.c`, boot firmware recognizing the magic/resume pointer, PowerPC 6xx/e300 SPRs, IMMR reset address rules, and cache-management helpers.

## Risks and Test Signals
Risks are severe: wrong BATs, cache state, flash mapping, resume magic, or save-area layout can brick resume. Test signals are deep-sleep/resume on supported PMC types, restored low RAM contents, correct timebase/decrementer after resume, and operation across low-boot/high-boot flash configurations.
