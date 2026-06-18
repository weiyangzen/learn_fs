# sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/self-refresh.S

## Purpose
This assembly routine runs from OCRAM during suspend to request SDRAM self-refresh, poll acknowledgements, execute WFI, then clear self-refresh on resume.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `socfpga_sdram_self_refresh`, `socfpga_sdram_self_refresh_sz`.
- Register/constant macro families: `SDR`(2), `SELFRFSHACK`(2), `SELFRSHREQ`(2), `MAX`(1); examples: `MAX_LOOP_COUNT`, `SDR_CTRLGRP_LOWPWREQ_ADDR`, `SDR_CTRLGRP_LOWPWRACK_ADDR`, `SELFRSHREQ_POS`, `SELFRSHREQ_MASK`, `SELFRFSHACK_POS`, `SELFRFSHACK_MASK`.

## Control Flow
Control flow is entered from C suspend code, runs with tight constraints, touches physical controller registers directly, waits or executes WFI, and returns to the caller with hardware state restored enough for C resume code to continue.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: suspend paths persist resume vectors and controller state across low-power entry; in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/linkage.h`, `asm/assembler.h`.
- Integrates with clocksource/clock framework setup during early platform initialization.

## Risks
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.

## Test Signals
- Build with the relevant SMP or suspend option enabled to assemble the entry code, then boot/suspend on hardware or a board model capable of exercising the path.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.

## Research Notes
- Read coverage: full file (3134 bytes, 126 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
