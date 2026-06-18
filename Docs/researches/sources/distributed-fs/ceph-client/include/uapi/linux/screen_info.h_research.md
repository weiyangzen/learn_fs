<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/screen_info.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/screen_info.h

Purpose: exports boot-time screen and framebuffer metadata used by architecture setup code, early consoles, and framebuffer drivers.

Important APIs, types, and functions: `struct screen_info` carries text-mode cursor and geometry, video page/mode, width/height/depth, framebuffer base and size, line length, capabilities, ext_lfb_base for 64-bit addresses, and EFI/VESA-related fields. Constants define legacy video types such as MDA, CGA, EGA/VGA, VESA LFB, architecture-specific framebuffers, EFI, video flags, and capability bits.

Control flow: boot loaders or firmware fill the structure before or during kernel entry. Early console and framebuffer initialization read it to choose text/video mode, locate the framebuffer, and decide whether quirks or 64-bit base handling are needed.

State and persistence behavior: the structure is boot-time state that becomes kernel global/arch state; it does not represent persistent storage. Values are often trusted early before full driver probing.

Dependencies and integration points: depends on Linux types and integrates with x86/EFI/VESA boot protocols, early printk/console, simplefb/efifb-like framebuffer setup, and platform video quirks.

Risks and edge cases: firmware may supply inconsistent dimensions, line length, depth, or framebuffer base. 64-bit base addresses require capability handling. Early consumers must avoid mapping invalid physical addresses or assuming text-mode fields are meaningful in graphics modes.

Test signals: boot with EFI framebuffer, VESA LFB, legacy VGA text, and no framebuffer; verify 64-bit framebuffer base, video type selection, line length/depth, and quirk skip behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/screen_info.h -->
