# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-mmio.h

## Purpose
`vgic-mmio.h` declares the common VGIC MMIO descriptor format, descriptor construction macros, access-size flags, address-to-INTID helpers, and shared MMIO/uaccess function prototypes used by the v2, v3, and ITS MMIO implementations.

## Important APIs, Types, And Functions
`struct vgic_register_region` describes one contiguous register region: offset, length, bits per IRQ, access flags, guest read/write callbacks, ITS-specific read/write callbacks, and optional userspace uaccess callbacks. `VGIC_ACCESS_8bit`, `VGIC_ACCESS_32bit`, and `VGIC_ACCESS_64bit` encode legal access sizes. `VGIC_ADDR_IRQ_MASK()` and `VGIC_ADDR_TO_INTID()` convert register offsets to interrupt IDs for per-IRQ registers. `REGISTER_DESC_WITH_BITS_PER_IRQ()`, `REGISTER_DESC_WITH_LENGTH()`, and `REGISTER_DESC_WITH_LENGTH_UACCESS()` build descriptor table entries.

The header exposes common helpers implemented in `vgic-mmio.c`, v3 utilities from `vgic-mmio-v3.c`, and table initializers for v2/v3 iodevs. It also declares `kvm_io_gic_ops`, the IO bus operations used by distributor, redistributor, CPU interface, and ITS devices.

## Control Flow
The header does not execute logic, but it defines the contract used by bsearch-based region lookup and dispatch. Descriptor arrays must be sorted by `reg_offset`, must describe either fixed-length registers or per-IRQ regions, and must set callbacks matching the iodev type. For per-IRQ descriptors, `bits_per_irq` determines both region length and address-to-INTID conversion.

## State And Persistence
No state is stored here. The header defines access contracts that protect persistent VGIC state in implementation files. The presence of separate guest MMIO and uaccess callbacks is a persistence-relevant ABI detail because migration may need different behavior than live guest register access.

## Dependencies And Integration Points
All listed VGIC MMIO files include this header. It integrates with KVM core types (`struct kvm_vcpu`, `struct kvm`, `struct vgic_its`, `struct vgic_io_device`), GIC register definitions from included C files, and VGIC runtime model helpers through prototypes.

## Risks
Descriptor macro misuse can silently expose the wrong register length or access width. `VGIC_ADDR_TO_INTID()` assumes power-of-two bits per IRQ, so adding unusual encodings would require a different helper. The unioned callback fields require the dispatcher to call the correct member for ITS versus non-ITS iodevs.

## Test Signals
Compile coverage is the primary signal. Runtime signals come from every `has_attr` and MMIO dispatch test that validates descriptor lookup, allowed widths, and per-IRQ INTID conversion for v2/v3 distributor and redistributor tables.
