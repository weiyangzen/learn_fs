# sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_nhmex.c

## Purpose

`uncore_nhmex.c` provides Nehalem-EX and Westmere-EX model-specific uncore PMU descriptions and callbacks. It defines MSR layouts, sysfs format/event attributes, PMU types, event constraints, and shared extra-register handling for Ubox, Cbox, Bbox, Sbox, Mbox, Rbox, and Wbox units.

## Important APIs, Types, And Functions

The only exported init hook is `nhmex_uncore_cpu_init()`, which selects Nehalem-EX versus Westmere-EX Mbox event aliases, clamps Cbox count to cores per package, and assigns `uncore_msr_uncores`.

Important callbacks include common MSR box/event operations (`nhmex_uncore_msr_*()`), Bbox/Sbox config and enable functions, complex Mbox shared-register helpers (`nhmex_mbox_get_shared_reg()`, `nhmex_mbox_get_constraint()`, `nhmex_mbox_hw_config()`, `nhmex_mbox_msr_enable_event()`), and Rbox constraint/config/enable functions. Static `intel_uncore_type` objects describe each box with counter counts, widths, MSR bases/offsets, event masks, constraints, shared-reg counts, format groups, and event aliases.

## Control Flow

The generic uncore framework calls `nhmex_uncore_cpu_init()` from `uncore.c` for EX CPU models. Later, `uncore_type_init()` and perf PMU registration consume `nhmex_msr_uncores`. Event initialization uses each type's `hw_config()` to map perf `config`, `config1`, and `config2` into `hw_perf_event_extra` registers. Counter assignment invokes type-specific `get_constraint()` where needed to reserve shared MSRs before an event can be scheduled. Event enable writes extra match/mask/config MSRs first, then writes the primary event control register with the required enable bit.

## State And Persistence Behavior

State is static platform description plus runtime shared-register state inside each `intel_uncore_box`. Mbox and Rbox shared registers use refcounts and raw spinlocks to allow compatible events to share registers and reject incompatible groupings. `uncore_nhmex` switches behavior for the Nehalem-EX versus Westmere-EX ZDP_CTL_FVC encoding and event aliases. Counts are accumulated by the common uncore polling path.

## Dependencies And Integration Points

The file depends on MSR access, `boot_cpu_data`, topology core count, common uncore helpers, perf extra-reg conventions, and sysfs event/format macros from `uncore.h`. It integrates with `uncore.c` through the `nhmex_uncore_cpu_init()` prototype and `uncore_msr_uncores`.

## Risks And Edge Cases

This file is dense with hardware-specific register encoding. Risks include conflicting shared extra-register users, incorrect alternative field selection for functionally identical Mbox/Rbox events, wrong enable-bit choice for different box families, and platform skew between NHM-EX and WSM-EX. Several event aliases use historical spellings, so changing names can break userspace scripts.

## Test Signals

Signals include PMU registration on Nehalem-EX/Westmere-EX, sysfs presence for all box types and aliases, perf group tests that intentionally collide or share Mbox/Rbox extra registers, validation of `config1`/`config2` match-mask events, and known workload counter sanity for QPI, memory, Bbox/Sbox, and Wbox clockticks.
