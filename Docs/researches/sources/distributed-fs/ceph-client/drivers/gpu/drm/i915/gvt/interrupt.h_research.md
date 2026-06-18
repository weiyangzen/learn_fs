# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/interrupt.h

## Purpose
`interrupt.h` declares the interrupt virtualization contract shared by MMIO handlers, display emulation, workload submission, and KVMGT. It enumerates virtual events and defines metadata structures used by `interrupt.c`.

## Important APIs, Types, And Functions
`enum intel_gvt_event_type` covers render/video/blitter/VECS events, display pipe events, flip done, PCH hotplug/AUX, PCU, and reserved/max sentinels. `gvt_event_virt_handler_t`, `struct intel_gvt_irq_ops`, `struct intel_gvt_event_info`, and `struct intel_gvt_irq` define the IRQ model. Public declarations include IRQ init, event trigger, interrupt-register handlers, and ring-id conversion helpers.

## Control Flow
No executable flow lives here. Consumers initialize `struct intel_gvt_irq`, fill mappings, use declared MMIO callbacks for guest interrupt-register writes, and raise events by enum.

## State And Persistence
The declared structures describe per-device IRQ metadata. Runtime guest state persists in `vgpu->mmio.vreg`; per-device mapping state persists in `struct intel_gvt_irq`.

## Dependencies And Integration Points
The header includes `linux/bitops.h` and forward-declares GVT structures. It is consumed by `interrupt.c`, `handlers.c`, display emulation, and workload paths.

## Risks
Enum reordering changes table indexing and derived flip-event mapping. `INTEL_GVT_EVENT_MAX` must continue to bound per-event arrays. Prototype drift would break link or runtime behavior.

## Test Signals
Compile coverage, valid ring-id-to-event mapping, no out-of-bounds event access, and successful guest handling of raised display/workload interrupts.
