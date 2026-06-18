<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/aspm.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/aspm.h

## Purpose

This header declares the HFI1 ASPM control interface, the module-visible ASPM mode variable, and the fast inline receive-context hook used by interrupt paths.

## Important APIs, types, and functions

`enum aspm_mode` defines `ASPM_MODE_DISABLED`, `ASPM_MODE_ENABLED`, and `ASPM_MODE_DYNAMIC`. The exported `aspm_mode` is the backing storage for the module parameter. Public functions initialize and exit ASPM handling, force hardware L1 off, disable or enable all contexts, and handle dynamic per-context disable through `__aspm_ctx_disable()`. The inline `aspm_ctx_disable()` checks `rcd->aspm_intr_supported` before calling the heavier implementation.

## Control Flow

The header shapes receive interrupt flow by keeping the unsupported path to one likely branch. Driver initialization calls `aspm_init()`, receive contexts call `aspm_ctx_disable()` on interrupts, PSM/context management can call all-context enable/disable helpers, and driver teardown calls `aspm_exit()`.

## State and Persistence

The header itself stores no state beyond declaring `aspm_mode`. It assumes ASPM fields exist in `struct hfi1_devdata` and `struct hfi1_ctxtdata`, supplied by `hfi.h`. Those fields and PCIe link registers are runtime-only.

## Dependencies and Integration Points

The header includes `hfi.h` and is consumed by HFI1 interrupt and initialization code. It integrates the ASPM implementation with receive-context data structures without exposing PCIe register details to callers.

## Risks

The inline fast path is in an interrupt-sensitive area, so adding work before the `likely(!rcd->aspm_intr_supported)` return would affect receive latency. The enum values are user-visible through the module parameter description; changing numeric values would break existing boot/module options.

## Test Signals

Build coverage should include all HFI1 users of `aspm_ctx_disable()`. Runtime signals are correct behavior for each `aspm` module parameter value, no measurable overhead when dynamic ASPM is unsupported, and clean calls through init, interrupt, all-context disable/enable, and exit paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/aspm.h -->
