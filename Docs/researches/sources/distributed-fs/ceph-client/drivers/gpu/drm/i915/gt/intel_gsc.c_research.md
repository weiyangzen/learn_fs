# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gsc.c

## Purpose
This file registers i915 Graphics Security Controller HECI interfaces as MEI auxiliary devices. It wires MMIO BAR resources, IRQ descriptors, optional extended operational memory, and HuC notifier integration for DG1/DG2-era GSC interfaces.

## Important APIs, Types, and Functions
Public entry points are `intel_gsc_init()`, `intel_gsc_fini()`, and `intel_gsc_irq_handler()`. Internal helpers include `gsc_init_one()`, `gsc_destroy_one()`, `gsc_irq_handler()`, `gsc_irq_init()`, `gsc_ext_om_alloc()`, `gsc_ext_om_destroy()`, and `gsc_release_dev()`.

`struct gsc_def` describes per-interface resources: MEI aux device name, HECI BAR offset, BAR size, polling mode, slow-firmware flag, and optional LMEM size. `gsc_def_dg1[]` exposes only HECI2 (`mei-gscfi`) while HECI1 is not implemented. `gsc_def_dg2[]` exposes HECI1 (`mei-gsc`) with a 4 MiB LMEM operational-memory object and HECI2 (`mei-gscfi`).

## Control Flow
`intel_gsc_init()` returns early when the device lacks HECI GSC support, then initializes both possible interfaces. `gsc_init_one()` skips non-primary tiles, skips HECI1 when PXP HECI is absent, selects a platform definition, allocates an IRQ descriptor unless polling is requested, allocates contiguous cleared LMEM for extended operational memory when required, fills `mei_aux_device` resources, initializes the auxiliary device, registers a HuC notifier for interface 0, and adds the device. Failures unwind through `gsc_destroy_one()`.

Interrupt handling receives GT IIR bits, maps bit 15 to interface 0 and bit 14 to interface 1, validates support/range, and forwards to the Linux generic IRQ layer for the per-interface IRQ descriptor.

## State and Persistence Behavior
Persistent state lives in `struct intel_gsc`: each interface records its `mei_aux_device`, optional LMEM GEM object, IRQ number, and ID. The LMEM object is pinned for the device lifetime and unpinned/dropped on teardown. Auxiliary devices persist until `intel_gsc_fini()` deletes and uninitializes them.

## Dependencies and Integration Points
The file integrates with Linux auxiliary bus and MEI aux devices, PCI resources, i915 platform feature flags (`HAS_HECI_GSC`, `HAS_HECI_PXP`), DG1/DG2 register offsets, local memory GEM allocation, HuC GSC notifier registration, GT IRQ dispatch, and PXP/GSC firmware consumers in other i915 modules.

## Risks
Resource description must match hardware exactly: wrong BAR offsets, sizes, or IRQ mapping prevent MEI communication. LMEM extended operational memory must be contiguous, pinned, and cleared. Multi-tile systems intentionally initialize only tile 0; changing that can expose nonfunctional devices. Failure unwind must avoid leaving auxiliary devices, notifiers, IRQ descriptors, or pinned GEM objects behind.

## Test Signals
Signals include MEI auxiliary devices appearing with expected names, successful GSC firmware/PXP/HuC flows, IRQ delivery on HECI events, clean init/fini unload cycles, no pinned-object leaks, correct behavior on DG1 versus DG2, and remote-tile systems skipping GSC initialization.
