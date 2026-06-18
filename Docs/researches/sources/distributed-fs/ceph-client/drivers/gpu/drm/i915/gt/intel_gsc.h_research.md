# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gsc.h

## Purpose
This header defines the i915 GT-side Graphics Security Controller interface state and public init/fini/IRQ entry points.

## Important APIs, Types, and Functions
`INTEL_GSC_NUM_INTERFACES` fixes the HECI interface count at two. `GSC_IRQ_INTF(_x)` maps interface IDs to GT interrupt bits, with HECI1 at bit 15 and HECI2 at bit 14. `struct intel_gsc` contains two `intel_gsc_intf` records, each holding a `mei_aux_device`, optional GEM object for scratch/operational memory, IRQ number, and interface ID. Public functions are `intel_gsc_init()`, `intel_gsc_fini()`, and `intel_gsc_irq_handler()`.

## Control Flow
The header has no executable control flow. GT initialization calls `intel_gsc_init()`, teardown calls `intel_gsc_fini()`, and GT interrupt handling calls `intel_gsc_irq_handler()` with the IIR bits.

## State and Persistence Behavior
The `intel_gsc` struct is embedded in `intel_gt` and persists for the GT lifetime. Interface fields are populated when auxiliary devices are registered and cleared during teardown.

## Dependencies and Integration Points
It forward-declares DRM/i915, GT, and MEI aux types and is included by GT type definitions and GSC implementation code. Its interrupt-bit mapping must match GT IRQ definitions and `intel_gsc.c`.

## Risks
Changing the interface count or IRQ bit mapping can break interrupt dispatch and MEI device setup. The header exposes lifetime-bearing pointers, so teardown must clear them consistently in the implementation.

## Test Signals
Build coverage, correct GT IRQ forwarding, auxiliary MEI device registration, and clean GSC teardown validate this interface.
