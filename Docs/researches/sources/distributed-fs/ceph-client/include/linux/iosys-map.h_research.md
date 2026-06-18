# sources/distributed-fs/ceph-client/include/linux/iosys-map.h

Purpose: This header defines `struct iosys_map`, an abstraction for code that can operate on either normal system memory or I/O memory through one typed handle.

Important APIs, types, and functions: `struct iosys_map` stores either `vaddr` or `vaddr_iomem` plus `is_iomem`. Initializers and setters include `IOSYS_MAP_INIT_VADDR`, `IOSYS_MAP_INIT_VADDR_IOMEM`, `IOSYS_MAP_INIT_OFFSET`, `iosys_map_set_vaddr`, and `iosys_map_set_vaddr_iomem`. Helpers cover equality/null checks, clear, increment, memcpy to/from, memset, typed read/write, and struct-field read/write.

Control flow: Every helper branches on `is_iomem` to choose normal memory operations (`memcpy`, `READ_ONCE`, `WRITE_ONCE`) or I/O operations (`memcpy_toio`, `readb/readw/readl/readq`, `write*`, `memset_io`). Offset initializers make shallow copies before incrementing.

State and persistence: The map is a lightweight caller-owned value. Clearing zeros it and returns it to NULL system-memory state. It does not manage allocation or mapping lifetime.

Dependencies and integration points: Depends on compiler types, `linux/io.h`, and string helpers. Used by DRM/dma-buf and drivers that pass buffers without exposing whether they live in system or MMIO memory.

Risks: Direct field access is discouraged because `is_iomem` must match the active pointer. Typed read/write only supports u8/u16/u32/u64 and may be unsafe for unaligned packed fields on strict architectures. Pointer arithmetic on `__iomem` is intentionally encapsulated here.

Test signals: Test system and I/O paths for copy, memset, increment, equality, NULL, typed access, field access, 32-bit u64 fallback, and offset initializer independence from the source map.
