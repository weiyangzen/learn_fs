# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm-asm-offsets.c

## Purpose
`pm-asm-offsets.c` generates assembly constants for AM33xx/AM43xx low-power SRAM code. It ensures hand-written assembly uses correct offsets into C structures shared with PM firmware support.

## Important APIs, Types, and Functions
The only function is `main()`, used by the kernel build offsets generator. It calls `ti_emif_asm_offsets()` and emits `DEFINE()` constants for fields in `struct am33xx_pm_sram_data` and `struct am33xx_pm_ro_sram_data`, plus structure sizes and a `BLANK()`.

## Control Flow
At build time, kbuild compiles/runs this offsets program to produce assembler include definitions. The generated constants are then consumed by AMx3 PM assembly/SRAM routines.

## State and Persistence Behavior
No runtime state exists. The persistent artifact is a generated header/assembly-offset output used during the same build.

## Dependencies and Integration Points
It depends on `linux/kbuild.h`, `linux/platform_data/pm33xx.h`, and `linux/ti-emif-sram.h`. It integrates with AM33xx/AM43xx suspend assembly and EMIF SRAM code.

## Risks
Missing or wrong offsets cause suspend assembly to read/write the wrong SRAM data fields, which can corrupt resume state, WFI flags, RTC base pointers, or L2 cache settings.

## Test Signals
Build AM33xx/AM43xx PM code and inspect generated offsets after structure changes. Runtime validation is successful standby/deepsleep suspend/resume with correct WFI flags, EMIF handling, RTC wake, and cache restore.
