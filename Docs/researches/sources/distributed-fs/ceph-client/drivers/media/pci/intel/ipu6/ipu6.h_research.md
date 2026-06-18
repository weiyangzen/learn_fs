# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6.h

## Purpose
This header defines the core IPU6 device identity, firmware names, hardware-version helpers, DMA/MMU limits, arbitration constants, MMU v2 trash-buffer workaround geometry, and the `struct ipu6_device` shared by the PCI parent and auxiliary children.

## Important APIs, Types, And Data
`enum ipu6_version` covers IPU6, IPU6SE, IPU6EP, and IPU6EP MTL. Inline helpers identify each version. Firmware names select generation-specific CPD blobs. `struct ipu6_device` stores the PCI device, child device list, ISYS/PSYS bus devices, buttress state, CPD firmware metadata, BAR base, reset/security flags, hardware version, and bus readiness. The header also defines MMU address limits, stream-cache limits, IOSF arbitration constants, DMA overshoot minimum, GDA page constants, and trash-buffer range/block offsets for MMU v2 invalidation.

## Control Flow
The header has no executable flow beyond inline version predicates. It provides constants that `ipu6.c`, `ipu6-mmu.c`, and ISYS code use during probe, firmware setup, MMU setup, and platform data initialization.

## State And Persistence
`struct ipu6_device` is the central in-memory state for the PCI device lifetime. Firmware and child pointers remain valid until remove unwinds them.

## Dependencies And Integration Points
It depends on Linux PCI/list types and `ipu6-buttress.h`. It is the common include for the IPU6 PCI, MMU, ISYS, and related support files.

## Risks And Test Signals
The hardware-version predicates gate register offsets, firmware names, port counts, and PHY callbacks; any new PCI ID must map to a correct version. MMU trash-buffer geometry is a hardware workaround and should be validated with DMA corruption tests and TLB invalidation stress.
