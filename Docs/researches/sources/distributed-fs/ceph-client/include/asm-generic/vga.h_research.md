# sources/distributed-fs/ceph-client/include/asm-generic/vga.h

Purpose: empty generic VGA compatibility include.

Important APIs/types/functions: none.

Control flow: none.

State and persistence: none.

Dependencies and integration points: satisfies `<asm/vga.h>` includes for architectures with no generic VGA-specific helpers.

Risks: VGA-capable architectures needing I/O address translation or legacy VGA hooks must provide an architecture-specific header.

Test signals: build coverage for framebuffer/console code on architectures using asm-generic.
