<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/aspm.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/aspm.c

## Purpose

This file controls PCIe ASPM L1 policy for HFI1. It supports disabled, enabled, and dynamic modes. Dynamic mode disables ASPM when receive context interrupts arrive close together, then re-enables ASPM after a timer expires without enough interrupt activity.

## Important APIs, types, and functions

The module parameter is `aspm`, backed by global `aspm_mode`. Public functions are `aspm_init()`, `aspm_exit()`, `aspm_hw_disable_l1()`, `__aspm_ctx_disable()`, `aspm_disable_all()`, and `aspm_enable_all()`. Internal helpers include `aspm_hw_l1_supported()`, `aspm_hw_set_l1_ent_latency()`, `aspm_hw_enable_l1()`, `aspm_enable()`, `aspm_disable()`, `aspm_disable_inc()`, `aspm_enable_dec()`, `aspm_ctx_timer_function()`, and `aspm_ctx_init()`.

## Control Flow

`aspm_init()` initializes the device ASPM spinlock, detects L1 support on both downstream and upstream PCIe components, initializes per-receive-context locks and timers for static contexts, programs a slower L1 entry latency, forces ASPM off, and then enables it if the selected mode allows. Dynamic per-context support is enabled only when hardware supports ASPM, mode is dynamic, and the context index is below `first_dyn_alloc_ctxt`.

Receive interrupt paths call the inline wrapper in the header, which enters `__aspm_ctx_disable()` only for supported contexts. That function records interrupt timestamps, detects two interrupts within `ASPM_TRIGGER_NS`, disables device ASPM through a counted global disable if needed, and schedules a one-second timer. The timer calls `aspm_enable_dec()` and re-enables ASPM only when all dynamic disable users have released their count. `aspm_disable_all()` stops per-context timers and interrupt processing before forcing ASPM off, while `aspm_enable_all()` re-enables hardware and resets per-context dynamic state.

## State and Persistence

State is volatile and stored in `hfi1_devdata` and `hfi1_ctxtdata`: `aspm_supported`, `aspm_enabled`, `aspm_lock`, `aspm_disabled_cnt`, per-context `aspm_lock`, `aspm_intr_supported`, `aspm_intr_enable`, `aspm_enabled`, timestamp fields, and timers. The only persistent-like input is the read-only module parameter value for the loaded module instance. Hardware state lives in PCIe link control/configuration registers until changed or reset.

## Dependencies and Integration Points

The file depends on PCIe capability accessors, HFI1 PCI config constants, HFI1 context lookup/refcount helpers, timers, atomics, spinlocks, and `is_ax()` hardware stepping detection. It integrates with receive interrupt handling via `aspm_ctx_disable()`, context initialization, PSM open/close behavior through all-context enable/disable, and driver unload through `aspm_exit()`.

## Risks

ASPM programming must touch downstream and upstream components in the documented order; reversing order can violate PCIe ASPM sequencing. Timer and interrupt races are controlled by per-context locks and a device count, so changes must preserve locking. `aspm_ctx_timer_function()` unconditionally marks the context enabled after decrementing the device count; double timer scheduling or missed timer deletion would corrupt the disable count. `aspm_disable_all()` resets the atomic count after disabling hardware, so it must remain synchronized with context timer deletion. Dynamic mode trades power for latency; too-low trigger thresholds or excessive rescheduling can cause performance or power regressions.

## Test Signals

Signals include module parameter coverage for `aspm=0`, `1`, and `2`, inspection of PCIe L1 enable bits on both endpoints, interrupt-heavy verbs workloads showing dynamic disable/re-enable, idle periods showing L1 returns after about one second, PSM context open/close paths disabling dynamic interrupt processing, suspend/resume or driver unload leaving ASPM enabled for power saving, and lockdep/timer debugging under interrupt storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/aspm.c -->
