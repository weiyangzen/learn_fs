
# sources/distributed-fs/ceph-client/arch/powerpc/perf/core-fsl-emb.c

## Purpose

This file implements the Freescale embedded PowerPC perf PMU core used by e500/e6500-style model drivers. It registers a `"cpu"` PMU, manages PMR counters and control registers, allocates restricted/nonrestricted counters, translates perf events through model-specific tables, handles overflows, and reserves PMU hardware.

## Important APIs, Types, And Functions

- `struct cpu_hw_events` tracks per-CPU active events, disabled state, and whether PMCs have been enabled.
- `ppmu` points to the active `struct fsl_emb_pmu` model backend.
- `read_pmc()`, `write_pmc()`, `write_pmlca()`, and `write_pmlcb()` access PMR counter and local control registers.
- `fsl_emb_pmu_read()` atomically accounts 32-bit counter deltas.
- `fsl_emb_pmu_disable()` freezes counters via `PMGC0_FAC`; `fsl_emb_pmu_enable()` enables interrupts/counter exceptions when events exist.
- `fsl_emb_pmu_add()` allocates a counter top-down, preserving restricted-capable counters when possible, programs PMC/PMLCA/PMLCB, and updates userpage state.
- `fsl_emb_pmu_del()`, `fsl_emb_pmu_start()`, and `fsl_emb_pmu_stop()` remove or control sampled counters.
- `fsl_emb_pmu_event_init()` translates hardware/cache/raw events via `ppmu`, validates restricted event capacity in groups, sets PMLCA freeze bits, initializes periods, and reserves hardware.
- `record_and_restart()` and `perf_event_interrupt()` account overflows and call `perf_event_overflow()`.
- `register_fsl_emb_pmu()` installs the model PMU and CPU hotplug prepare callback.

## Control Flow

A model driver calls `register_fsl_emb_pmu()`. On event initialization, generic/cache/raw events are translated by the model `xlate_event()` and checked for validity/restriction. Adding an event disables the PMU, finds a usable counter, initializes count and state, writes PMC/PMLCB/PMLCA, and re-enables the PMU. Reads account 32-bit deltas. Interrupt handling scans all model counters for negative values, restarts active overflowed events, clears inactive overflowed counters, sets `MSR_PMM`, and re-enables PMGC0 interrupt/freeze behavior.

## State And Persistence

Per-CPU state is in `cpu_hw_events`. Global hardware reservation state is in `num_events` and `pmc_reserve_mutex`. Per-event state is in `event->hw.idx`, `config`, `config_base`, `prev_count`, `period_left`, and `state`. The PMU hardware registers persist programmed event selection until changed or cleared.

## Dependencies And Integration Points

It depends on `asm/reg_fsl_emb.h` PMR definitions, generic perf PMU callbacks, PowerPC PMU reservation hooks, firmware/hardware PMC enable hooks, CPU hotplug state `CPUHP_PERF_POWER`, and model data from `e500-pmu.c`/`e6500-pmu.c`.

## Risks And Edge Cases

Restricted counters are capacity-checked but there is a TODO to migrate nonrestricted events if restricted needs change. Counter allocation from the top down is important for restricted events. Counters are 32-bit, so delta masking must remain correct. Interrupt handling assumes negative counter values indicate overflow. Exclude idle is unsupported. Hardware reservation must be balanced by `event->destroy`.

## Test Signals

Use `perf stat` and sampling on e500/e6500 systems for generic, cache, raw, restricted threshold events, group capacity failures, add/delete/start/stop paths, and overflow sampling. Build and boot test `CONFIG_FSL_EMB_PERF_EVENT` with both model drivers.
