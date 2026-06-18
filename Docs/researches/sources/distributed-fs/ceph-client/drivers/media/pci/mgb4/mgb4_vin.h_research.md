# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_vin.h

- Purpose: Data structures and lifecycle declarations for one MGB4 video input endpoint.
- Important APIs/types/functions: `struct mgb4_vin_regs`, `struct mgb4_vin_config`, `struct mgb4_vin_dev`, `mgb4_vin_create`, and `mgb4_vin_free`.
- Control flow: Implementation uses config register offsets and IRQ/channel IDs to create each input; other modules use `mgbdev->vin[]` pointers for loopback and sysfs coordination.
- State and persistence: Endpoint state includes V4L2/vb2 objects, locks, buffer list, works, timings, frequency range, padding, deserializer client, config pointer, and debugfs register metadata.
- Dependencies and integration points: Integrated by core, vout loopback, input sysfs, CMT, and DMA code.
- Risks: Any struct layout change affects multiple modules. Debugfs register array sizing assumes `mgb4_vin_regs` is only 32-bit fields.
- Test signals: Compile plus capture endpoint creation/free tests.
