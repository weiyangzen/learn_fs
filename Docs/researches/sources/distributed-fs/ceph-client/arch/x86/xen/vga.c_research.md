<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/vga.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/vga.c

## Purpose
Translates Xen dom0 VGA console metadata into Linux `screen_info` so early console and framebuffer setup can use text, VESA LFB, or EFI LFB details supplied by Xen.

## Important APIs, Types, And Functions
The entry point is `xen_init_vga(const struct dom0_vga_console_info *info, size_t size, struct screen_info *screen_info)`.

## Control Flow
The function initializes conservative VGA text defaults, then switches on `info->video_type`. Text mode updates rows, columns, cursor, and font height after validating the structure size. VESA/EFI LFB updates dimensions, depth, framebuffer base/size, line length, color masks, 64-bit base capability, and optional VESA mode attributes; EFI LFB sets `VIDEO_TYPE_EFI`.

## State And Persistence
It only mutates the caller-provided `screen_info`, which persists as boot/video configuration. No durable storage is touched.

## Dependencies And Integration Points
Depends on Xen `dom0_vga_console_info`, Linux `screen_info`, and x86 setup video constants. It is called from Xen x86 boot setup paths for initial domain console discovery.

## Risks And Edge Cases
Size checks prevent reading missing union members, but unsupported or truncated records leave defaults. Incorrect Xen-provided LFB base, color masks, or line length can break early framebuffer output. Extended LFB base is used only when present and nonzero.

## Test Signals
Boot dom0 with text VGA, VESA LFB, and EFI LFB; verify `screen_info`, early console, fbcon/efifb handoff, 64-bit framebuffer base handling, and truncated metadata fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/vga.c -->
