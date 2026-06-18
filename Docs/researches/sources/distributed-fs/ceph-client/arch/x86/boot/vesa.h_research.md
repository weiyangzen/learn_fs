# sources/distributed-fs/ceph-client/arch/x86/boot/vesa.h

Purpose: defines packed VESA BIOS Extension structures used by boot video probing.

Important APIs and state: declares `far_ptr`, `struct vesa_general_info`, `VESA_MAGIC`, and `struct vesa_mode_info`.

Control flow: no runtime logic; structure layout must match VBE BIOS ABI.

Dependencies and integration: used by `video-vesa.c` to call VBE functions, enumerate modes, store framebuffer geometry, and retrieve EDID.

Risks and test signals: packing or field-size errors corrupt BIOS data interpretation. Test VESA text and linear-framebuffer mode detection across BIOS/firmware implementations.
