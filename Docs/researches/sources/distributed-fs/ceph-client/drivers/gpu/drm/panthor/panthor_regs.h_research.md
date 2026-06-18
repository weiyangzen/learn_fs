# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_regs.h

## Purpose
Defines Panthor GPU, job, MMU, CSF doorbell, and PWR_CONTROL register offsets and bitfield helpers. It is the shared hardware contract for the Panthor driver.

## Important APIs, Types, and Functions
This is macro-only. Major groups cover GPU identity/features/interrupts/commands/status, shader/tiler/L2 present/ready/power registers, coherency and MCU control, job interrupt registers, MMU interrupt and per-AS register windows, `AS_TRANSCFG`/`AS_MEMATTR` encodings, CSF latest flush and doorbells, and PWR interrupt/status/command/domain registers.

## Control Flow
Consumer code uses these constants to build register reads/writes. Examples include MMU AS programming through `AS_TRANSTAB()`, `AS_MEMATTR()`, and `AS_COMMAND()`, scheduler doorbells through `CSF_DOORBELL()`, GPU cache flush command construction with `GPU_FLUSH_CACHES()`, and PWR domain commands with `PWR_COMMAND_DEF()`.

## State and Persistence
The file contains no software state. It defines how persistent hardware state is addressed and decoded, including feature registers, IRQ masks, MMU fault status, power readiness, transition and delegation state, and command encodings.

## Dependencies and Integration Points
Requires Linux bit helpers such as `BIT`, `BIT_U64`, and `GENMASK`. It is included by Panthor GPU, MMU, scheduler, firmware, and power code. Its offsets are based on Arm Mali register maps and must match hardware/firmware expectations.

## Risks and Edge Cases
Incorrect bit shifts or offsets can silently corrupt hardware control. `GPU_COHERENCY_PROT_BIT(name)` relies on token pasting with defined protocol names. AS slot macros assume `MMU_AS_SHIFT` layout. PWR domain IDs double as allowed/delegated bit positions, making command/status coupling important.

## Test Signals
Signals include successful probe feature detection, IRQ handling, MMU AS updates, cache flush completion, CSF job doorbells, PWR domain transitions, and register-level debug traces on real hardware or emulation.
