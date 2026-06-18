# sources/distributed-fs/ceph-client/drivers/firmware/efi/sysfb_efi.c

Purpose: Applies EFI framebuffer quirks and firmware-node links for generic system framebuffer registration. It compensates for broken EFI framebuffer descriptors on known systems, especially older Apple hardware and portrait-panel devices.

Important APIs/types/functions: `efifb_dmi_list` stores per-model fallback base, stride, width, height, and override flags. `efifb_setup_from_dmi()` supports boot option lookup. `efifb_set_system()` applies DMI data and validates hard-coded framebuffer bases against VGA PCI BARs. `sysfb_apply_efi_quirks()` drives DMI matching, and `sysfb_set_efifb_fwnode()` attaches a fwnode that can add DT PCI dependency links.

Control flow: During sysfb setup, quirks are skipped or applied based on `orig_video_isVGA` and `VIDEO_CAPABILITY_SKIP_QUIRKS`. DMI callbacks either fill missing framebuffer fields or swap width/height for portrait devices. In DT mode, fwnode `add_links` scans PCI host ranges and links efifb to the PCI controller that owns the memory window.

State and persistence behavior: Mutates the global primary `screen_info` fields for framebuffer base, dimensions, stride, size, and video type. No persistent storage is written; the state affects later platform-device registration and framebuffer driver binding.

Dependencies and integration points: Uses DMI, EFI screen info, PCI resource APIs, OF PCI range parsing, sysfb, and VGA video constants. Downstream consumers include simplefb, corebootdrm/DRM, efifb, and sysfb platform-device creation.

Risks and test signals: Incorrect DMI matches can corrupt display geometry; wrong base validation can suppress a valid boot console; DT fwnode links can affect probe order. Test signals include booting listed systems, verifying `/proc/iomem` reservations and framebuffer dimensions, checking portrait device rotation fixups, and ensuring PCI-backed framebuffers do not conflict with host bridge windows.
