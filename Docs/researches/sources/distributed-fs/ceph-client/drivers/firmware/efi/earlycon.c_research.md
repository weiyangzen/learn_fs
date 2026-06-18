# sources/distributed-fs/ceph-client/drivers/firmware/efi/earlycon.c

Purpose: provides `earlycon=efifb`, a framebuffer-backed EFI early console that renders text directly into a 32-bpp EFI framebuffer before the normal console stack is ready.

Important APIs/types/functions: registers `EARLYCON_DECLARE(efifb, efi_earlycon_setup)`. Helpers include `efi_earlycon_remap_fb()`, `efi_earlycon_unmap_fb()`, `efi_earlycon_map()`, `efi_earlycon_clear_scanline()`, `efi_earlycon_scroll_up()`, `efi_earlycon_write_char()`, `efi_earlycon_write()`, and `efi_earlycon_reprobe()`.

Control flow: setup validates EFI video type and 32-bpp depth, computes the framebuffer base including high bits, chooses writeback mapping for the `ram` option or write-combine otherwise, selects a default font, scrolls the boot text area, and installs the console write callback. Before early ioremap disappears, an early initcall remaps the full framebuffer with `memremap()` if the boot console is still registered; a late initcall unmaps it unless `keep_bootcon` kept it active.

State and persistence behavior: global cursor position, font, framebuffer mapping, line-width cache, framebuffer base, and mapping mode track console state. The mapping persists through boot-console lifetime.

Dependencies and integration points: depends on `sysfb_primary_display`, font library, early_ioremap/memremap, console registration, and EFI stub/platform display table setup.

Risks and test signals: only 32-bpp framebuffers are supported, and incorrect line-length/base/size data can corrupt memory. Scrolling uses cached maximum x widths to reduce copying. Test signals include visible early boot text with `earlycon=efifb`, correct behavior with `keep_bootcon`, and no setup on non-EFI or non-32-bpp displays.
