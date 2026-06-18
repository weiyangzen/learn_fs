# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/agp_backend.h

This header defines Alpha-specific AGP backend data structures. `alpha_agp_mode` overlays AGP capability/mode bits over a 32-bit longword, including rate, fast-write, 4GB, enable, sideband addressing, and request queue depth. `alpha_agp_info` binds a PCI hose, aperture bus base/size/sysdata, capability and active mode, private state, and operation table.

`struct alpha_agp_ops` is the main API: chipset backends provide `setup`, `cleanup`, `configure`, `bind`, `unbind`, and DMA-address `translate` callbacks. Integration is through `alpha_machine_vector.agp_info`, PCI controller code, and generic AGP memory management. State is held in the info object and backend private data, with hardware aperture programming performed by implementations elsewhere.

Risks are ABI drift between generic AGP and Alpha hose/aperture assumptions, incorrect bitfield layout assumptions, and stale chipset operations. Tests are build coverage plus AGP backend initialization/bind/unbind paths on supported chipsets.
