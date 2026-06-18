<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/btext.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/btext.c

Purpose: Implements early boot framebuffer text output for PowerPC BootX/Open Firmware displays and hooks it into udbg.

Important APIs/types/functions: Display globals, `btext_prepare_BAT()`, `btext_setup_display()`, `btext_unmap()`, `btext_map()`, `btext_find_display()`, `btext_update_display()`, clear/flush helpers, character drawing routines, `btext_drawchar/string/text/hex()`, and `udbg_init_btext()`.

Control flow: Early boot discovers display properties from OF/BootX, maps the framebuffer, tracks an 8x16 text cursor, draws glyphs into 8/16/32-bit framebuffers, wraps or clears lines, flushes cache lines, and exposes `btext_drawchar` as `udbg_putc`.

State and persistence: Persistent early-boot state includes framebuffer physical/logical base, row bytes, depth, rectangle, cursor coordinates, maximum text cells, BAT mapping values, and mapped flag.

Dependencies and integration points: Depends on OF device nodes, memblock/pgtable/io mapping, font data, BootX setup, RMCI helpers on PPC64 early debug, and udbg.

Risks: Runs before normal console and memory mapping are stable. Wrong pitch/depth/address can write arbitrary memory; mapping/unmapping must match early MMU state.

Test signals: CONFIG_BOOTX_TEXT builds, old PowerMac/OF boot display smoke tests, early printk/udbg output, framebuffer mode update tests, and cache flush validation.

Source read size: 585 lines, 13701 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/btext.c -->
