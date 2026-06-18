# sources/distributed-fs/ceph-client/include/linux/ioremap.h

Purpose: This header provides a helper to identify whether an address lies in the architecture's ioremap virtual address area.

Important APIs, types, and functions: `is_ioremap_addr(const void *x)` strips KASAN pointer tags with `kasan_reset_tag` and compares against `IOREMAP_START` and `IOREMAP_END`. If the architecture does not define them, they default to `VMALLOC_START` and `VMALLOC_END` when I/O memory or generic ioremap support is enabled.

Control flow: Enabled configurations perform a range check; unsupported configurations always return false.

State and persistence: No state is stored. The function depends on compile-time address range constants.

Dependencies and integration points: Depends on KASAN tag handling, architecture page table/vmalloc definitions, and generic ioremap support. Used by debug, memory-management, or sanitizer code that must classify virtual addresses.

Risks: Some architectures may use ioremap space outside generic vmalloc defaults and must override the range. Tagged pointers must be reset before comparison. False classification can misroute memory handling or diagnostics.

Test signals: Build on generic and arch-overridden ioremap ranges, KASAN tagged pointer checks, boundary addresses at start/end, and disabled `CONFIG_HAS_IOMEM`/`CONFIG_GENERIC_IOREMAP`.
