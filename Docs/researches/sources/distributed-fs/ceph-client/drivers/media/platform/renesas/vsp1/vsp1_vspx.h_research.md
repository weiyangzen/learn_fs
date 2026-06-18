# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_vspx.h

Purpose: declares the internal VSPX initialization and cleanup hooks for the VSP1 device driver.

Important APIs/types: includes `vsp1.h` and declares `vsp1_vspx_init(struct vsp1_device *vsp1)` and `vsp1_vspx_cleanup(struct vsp1_device *vsp1)`.

Control flow/state: no state is defined here; implementation allocates and initializes `vsp1->vspx`.

Dependencies/integration: used by VSP1 probe/remove paths when Gen4 VSPX support is present. The public ISP API is exported from the C file through `include/media/vsp1.h`, not this internal header.

Risks and test signals: compile-time integration depends on `struct vsp1_device` visibility. Test device probe/remove on VSPX-capable hardware and configurations where VSPX is absent.
