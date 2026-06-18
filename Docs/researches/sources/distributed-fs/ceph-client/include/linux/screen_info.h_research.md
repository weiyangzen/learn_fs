# sources/distributed-fs/ceph-client/include/linux/screen_info.h

Purpose: `screen_info.h` provides kernel helpers for interpreting boot-time `struct screen_info` framebuffer and text-console metadata. It bridges architecture/UAPI boot parameters into resource reservation, pixel format detection, VGA/VBE/EFI framebuffer handling, and optional PCI fixups.

Important APIs/types/functions: Inline helpers include `__screen_info_has_lfb()`, `__screen_info_lfb_base()`, `__screen_info_set_lfb_base()`, `__screen_info_lfb_size()`, `__screen_info_vbe_mode_nonvga()`, `__screen_info_video_type()`, `screen_info_video_type()`, and `__screen_info_vesapm_info_base()`. Exported declarations include `screen_info_resources()`, `__screen_info_lfb_bits_per_pixel()`, `screen_info_pixel_format()`, `screen_info_apply_fixups()`, and `screen_info_pci_dev()`.

Control flow: Consumers inspect `screen_info_video_type()` first to classify initialized display output. Linear framebuffer helpers then compute base and size, including the special VESA size shift and optional 64-bit base extension. Resource builders and framebuffer drivers call the non-inline helpers to reserve memory, decode pixel formats, and discover matching PCI devices when PCI is enabled.

State and persistence behavior: The helpers operate on caller-provided `struct screen_info`. `__screen_info_set_lfb_base()` mutates the base fields and toggles `VIDEO_CAPABILITY_64BIT_BASE`; other inline helpers are read-only. Boot-time screen info persists as early console/framebuffer discovery state, but this header owns no storage.

Dependencies and integration points: It depends on UAPI `linux/screen_info.h`, bit macros, resource management, PCI, and framebuffer/pixel-format code. Integration points include simplefb/simpledrm, VGA arbitration, EFI framebuffer setup, and early architecture boot parameter parsing.

Risks: Misclassifying `orig_video_isVGA` can reserve or touch VGA resources incorrectly. 64-bit framebuffer bases require both low and extended fields to be coherent. VESA VLFB size is encoded differently from EFI, and `vesapm_seg` below `0xc000` is intentionally rejected.

Test signals: Cover EFI and VESA linear framebuffers, legacy text modes, non-VGA VBE bit 5, 64-bit framebuffer bases, zero or unknown video type, PCI-disabled stubs, and resource counts up to `SCREEN_INFO_MAX_RESOURCES`.
