<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vga.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vga.h

Purpose: Provides PowerPC VGA/MDA text-mode video memory access helpers with correct little-endian cell handling.

Important APIs/types/functions: `scr_writew()`, `scr_readw()`, `scr_memsetw()`, `VGA_MAP_MEM()`, `vga_readb()`, and `vga_writeb()`.

Control flow: When VGA or MDA console is enabled, console code reads/writes 16-bit screen cells through endian-converting helpers; PPC64 maps physical VGA memory through `ioremap`, while 32-bit keeps the passed address.

State and persistence: State is external VGA text memory. The header owns no buffers but writes directly to mapped framebuffer cells.

Dependencies and integration points: Depends on `asm/io.h`, endian conversion helpers, and vt buffer integration. Used by VGA/MDA console code.

Risks: VGA text cells are little-endian regardless of CPU endian mode. Missing conversion corrupts characters/attributes; wrong mapping on PPC64 can access physical memory incorrectly.

Test signals: VGA/MDA console build and boot tests, text rendering checks on big-endian and little-endian PowerPC, and sparse/compile coverage for non-console configs.

Source read size: 55 lines, 1159 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vga.h -->
