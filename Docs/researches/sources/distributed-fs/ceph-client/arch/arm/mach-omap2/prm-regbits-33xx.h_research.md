# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm-regbits-33xx.h

## Purpose
Defines AM33xx PRM bit masks for powerdomain memory state, logic retention/status, low-power state requests, reset control, and previous power-state tracking.

## APIs, Flow, And State
Macro-only definitions cover GFX, PRUSS, MPU L1/L2/RAM, PER memory, RAM memory, `AM33XX_LOWPOWERSTATECHANGE`, `AM33XX_LASTPOWERSTATEENTERED`, logic retention/status, and global warm/cold reset bits. No executable state.

## Dependencies And Integration
Includes `prm.h` and is consumed by `prm33xx.c` powerdomain operations and AM33xx reset code. The masks map `struct powerdomain` mask arrays to actual PRM registers.

## Risks And Test Signals
Bank-specific masks are used through generic powerdomain callbacks; an incorrect mask can silently program the wrong retention/on state. Test signals are AM33xx suspend/resume, powerdomain previous-state reads, and warm/cold reboot mode behavior.
