# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/debug-sr.c

## Purpose

This nVHE file extends common debug register switching with host SPE/TRBE trace-buffer save, drain, disable, and restore handling.

## Important APIs, Types, And Functions

Important helpers include `__debug_save_spe()`, `__debug_restore_spe()`, `__trace_do_switch()`, `__trace_drain_and_disable()`, and corresponding trace restore logic later in the file, plus public nVHE debug switch entry points.

## Control Flow

When switching away from the host, the code saves SPE buffer/control state if enabled, disables data generation, drains buffered data with `psb_csync()`/`dsb`, disables profiling buffers, switches TRFCR, drains TRBE if active, and handles CPU workaround 2064142 with an extra drain. Restore reverses buffer/control registers after synchronization.

## State And Persistence Behavior

State is stored in per-CPU `host_debug_state` fields such as `pmscr_el1`, `pmblimitr_el1`, and `trblimitr_el1`. It also touches live SPE/TRBE/TRFCR sysregs and host-data flags.

## Dependencies And Integration Points

It depends on common `hyp/debug-sr.h`, protected-mode flags, SPE/TRBE feature bits, trace barriers, and nVHE world-switch paths.

## Risks And Test Signals

Risks are host trace DMA after stage-2/trap changes, lost profiling data, missing workaround drain, and exposing host tracing buffers to protected guests. Test signals are SPE/TRBE enabled on host while running guests, protected-mode transitions, trace-buffer drain validation, and debug-register switch tests.
