
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/gop.c

Purpose: parses `video=efifb:` graphics options, selects an EFI Graphics Output Protocol mode, populates Linux `screen_info`, and copies EDID data for the primary display.

Important APIs/types/functions: exports `efi_parse_option_graphics()` and `efi_setup_graphics()`. Internal mode selectors include `choose_mode_modenum()`, `choose_mode_res()`, `choose_mode_auto()`, `choose_mode_list()`, `set_mode()`, `setup_screen_info()`, `setup_edid_info()`, and `find_handle_with_primary_gop()`.

Control flow: option parsing recognizes `mode=N`, `WxH[-depth|rgb|bgr]`, `auto`, and `list`. Setup locates all GOP handles, chooses a GOP that also supports ConOut when possible, applies requested mode changes, fills framebuffer base, resolution, stride, depth, pixel bit positions, 64-bit base capability, and skip-quirks flag, then reads active or discovered EDID protocol data.

State and persistence behavior: static `cmdline` stores the requested graphics policy until setup. Resulting framebuffer/EDID state is persisted into `screen_info`/`edid_info` or a primary display config table consumed by the kernel.

Dependencies and integration points: depends on EFI GOP, EDID protocols, console input for `list`, EFI printing/key wait, and Linux `screen_info`/sysfb consumers. It is called by common and x86 EFI stubs.

Risks and test signals: firmware may expose splitter GOP handles, BLT-only modes, invalid pixel formats, or missing EDID. `auto` chooses maximum area and depth, which may select modes firmware cannot set reliably. Test signals include explicit mode numbers, resolution/depth matching, list timeout/key path, primary ConOut selection, 64-bit framebuffer bases, bitmask pixel formats, and EDID active/discovered fallback.
