# sources/distributed-fs/ceph-client/arch/hexagon/kernel/vmlinux.lds.S

## Purpose

`vmlinux.lds.S` is the Hexagon architecture linker script for the kernel image. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

It defines image layout, section placement, alignment, init sections, per-CPU data, exception tables, and architecture-specific symbols consumed by boot/MM code. Concrete declarations observed in the file: Includes: `asm-generic/vmlinux.lds.h`, `asm/asm-offsets.h`, `asm/mem-layout.h`, `asm/cache.h`, `asm/thread_info.h`. Macros: `PAGE_SIZE`. Assembly entry labels: `stext`.

## Control Flow, State, And Persistence

Build-time only: the linker script lays out the final `vmlinux`; runtime code uses symbols such as text/data boundaries and initial stack/table locations.

## Dependencies And Integration Points

It integrates with generic linker macros, `head.S`, `mm/init.c`, and generated offsets.

## Risks And Test Signals

Risks are section misalignment, discarded required metadata, or address mismatch with early mappings. Test signals are successful link, `readelf -S`, boot, module exception-table behavior, and init memory freeing.
 A local static signal for this file is that it has 71 lines and 1350 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
