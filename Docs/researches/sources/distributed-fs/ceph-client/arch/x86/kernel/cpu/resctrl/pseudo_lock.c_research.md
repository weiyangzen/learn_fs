# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/pseudo_lock.c

## Purpose

This file provides x86-specific pseudo-locking primitives for resctrl. Pseudo-locking uses CAT to load a kernel buffer into a selected cache allocation region and keep later allocations from overlapping it, then exposes measurement helpers to evaluate latency and cache residency.

## Important APIs, Types, And Functions

Important APIs are `resctrl_arch_get_prefetch_disable_bits()`, `resctrl_arch_pseudo_lock_fn()`, `resctrl_arch_measure_cycles_lat_fn()`, `resctrl_arch_measure_l2_residency()`, and `resctrl_arch_measure_l3_residency()`. It uses `struct pseudo_lock_region`, per-CPU `pqr_state`, `MSR_MISC_FEATURE_CONTROL`, `MSR_IA32_PQR_ASSOC`, perf raw events, RDPMC, and tracepoints from `pseudo_lock_trace.h`.

## Control Flow

Platform detection returns the documented prefetch-disable bits for validated Intel Broadwell-X and Goldmont variants. The lock function flushes caches with `wbinvd()`, disables interrupts and hardware prefetchers, switches PQR_ASSOC to the pseudo-lock CLOSID, reads the buffer by page and cache-line stride, restores the previous CLOSID/RMID and prefetch MSR, then wakes the waiting control thread. Measurement paths either trace per-access TSC latency or create pinned perf counters for platform-specific hit/miss events, read the locked region, compute deltas, and emit L2/L3 tracepoints.

## State, Dependencies, And Integration

The only global state is `prefetch_disable_bits`. Runtime state lives in `pseudo_lock_region`, perf events, and trace buffers. Dependencies include resctrl pseudo-lock generic code, x86 perf raw event encoding, MSRs, interrupt/preemption rules, cache flushing, and tracepoint generation.

## Risks And Test Signals

The code is sensitive to platform event encodings, prefetch bits, interrupt state, speculative reads, and KASAN register pressure. Bad restore paths can leave prefetchers or PQR_ASSOC in the wrong state. Test on supported platforms by creating pseudo-locked regions, reading `tracefs` events for latency/L2/L3, validating low miss rates under load, and checking unsupported platforms reject pseudo-locking cleanly.
