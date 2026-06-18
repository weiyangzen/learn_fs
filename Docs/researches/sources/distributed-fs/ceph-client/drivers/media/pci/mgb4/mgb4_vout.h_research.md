# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_vout.h

- Purpose: Data structures and lifecycle declarations for one MGB4 video output endpoint.
- Important APIs/types/functions: `struct mgb4_vout_regs`, `struct mgb4_vout_config`, `struct mgb4_vout_dev`, `mgb4_vout_create`, and `mgb4_vout_free`.
- Control flow: Core creates outputs when module type supports them; sysfs and vin loopback code inspect and mutate output device state.
- State and persistence: Endpoint state includes V4L2/vb2 objects, locks, buffer list, DMA work, width/height/frequency/padding, serializer client, config pointer, and debugfs register metadata.
- Dependencies and integration points: Integrated with core, sysfs_out, CMT, DMA, and vin loopback helpers.
- Risks: Struct fields are shared across modules without accessors, so changes require synchronized updates. Debugfs array sizing assumes only 32-bit register fields.
- Test signals: Compile plus output endpoint creation/free and loopback tests.
