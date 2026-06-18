# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_irq.h

Purpose: Declares PXP interrupt bits and optional IRQ helper APIs.

Important APIs/types: Interrupt bit macros for terminated, firmware-requested app termination, and reset complete; `GEN12_PXP_INTERRUPTS`; declarations/stubs for enable, disable, and handler.

Control flow: Header-only conditional compilation.

State/persistence: None.

Dependencies/integration: Used by PXP hardware init/fini, GT IRQ dispatch, debugfs, and session worker.

Risks: Interrupt bit definitions must match hardware KCR IIR layout. Disabled-config stubs make calls no-ops.

Test signals: Build across configs and interrupt-driven PXP recovery.
