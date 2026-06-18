# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc-compat.h

## Purpose

`dispc-compat.h` is the small internal header for DISPC compatibility helpers. The complete 19-line file was read. It declares synchronous manager enable/disable, wait-for-IRQ, and IRQ init/uninit functions implemented by `dispc-compat.c`.

## Important APIs, Types, and Functions

Declared APIs are `dispc_mgr_enable_sync()`, `dispc_mgr_disable_sync()`, `omap_dispc_wait_for_irq_interruptible_timeout()`, `dss_dispc_initialize_irq()`, and `dss_dispc_uninitialize_irq()`.

## Control Flow

The header has no runtime control flow. It allows `apply.c` and related DSS code to call the IRQ compatibility layer without exposing implementation details.

## State and Persistence Behavior

No state is defined here; state lives in `dispc-compat.c` and DISPC hardware registers.

## Dependencies and Integration Points

The declarations rely on OMAP DSS enum and integer types available through the surrounding DSS include graph. It is included by `apply.c` and `dispc-compat.c`.

## Risks and Edge Cases

The header does not include a type header itself, so include order must provide `enum omap_channel`, `u32`, and `unsigned long`. Any signature change must be kept in sync with `dispc-compat.c` and callers.

## Test Signals

Signals are compile-only: include-order builds, warnings as errors, and successful linking of `apply.o` with `dispc-compat.o`.
