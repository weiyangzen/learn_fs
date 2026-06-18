# sources/distributed-fs/ceph-client/include/linux/mfd/syscon/atmel-mc.h

## Purpose

This 140-line header defines legacy Atmel AT91 memory controller, EBI, SMC, SDRAMC, and burst flash controller register offsets and bitfields.

## Important APIs, Types, and Functions

It exports reset/abort status fields, master priority, EBI chip-select/config, SMC timing and mode fields, SDRAM mode/timing/control/refresh/low-power/interrupt fields, and burst flash controller mode fields.

## Control Flow

No code flow exists. Platform and memory-controller code writes timing, bus width, refresh, low-power, and chip-select fields through syscon or MMIO access.

## State and Persistence Behavior

These registers persist memory controller configuration that directly affects external memory, SDRAM refresh, bus width, wait states, and abort reporting.

## Dependencies and Integration Points

It integrates Atmel syscon/memory-controller users with EBI, SMC, SDRAMC, BFC, boot, and external memory setup code.

## Risks and Edge Cases

The macros `AT91_MPR_MSTP(n)` and `AT91_MC_EBI_CS(n)` reference `x` instead of the formal parameter, which is a latent macro bug if used. Timing and refresh misconfiguration can break memory access.

## Test Signals

Compile tests for macro users, external memory timing validation, SDRAM refresh tests, and static analysis for unused/broken parameter macros.
