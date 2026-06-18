# sources/distributed-fs/ceph-client/net/core/mp_dmabuf_devmem.h

Purpose: Declares the page-pool dmabuf device-memory provider interface used when `CONFIG_NET_DEVMEM` is enabled, and provides no-op/error inline stubs when it is disabled.

Important APIs, types, and functions: Enabled builds declare `mp_dmabuf_devmem_init()`, `mp_dmabuf_devmem_alloc_netmems()`, `mp_dmabuf_devmem_destroy()`, and `mp_dmabuf_devmem_release_page()`. Disabled builds inline `init` as `-EOPNOTSUPP`, allocation as `0`, destroy as no-op, and release as `false`.

Control flow: There is no runtime control flow in the header beyond compile-time selection. Callers can use the API unconditionally and rely on stubs to report unsupported device memory.

State and persistence: State is held by the page pool and implementation compiled elsewhere when enabled. This header stores no state and has no persistence.

Dependencies and integration points: Includes `net/netmem.h` and operates on `struct page_pool` and `netmem_ref`. It integrates with page-pool receive memory, dmabuf-backed device memory, and network drivers capable of using devmem-backed buffers.

Risks: Callers must treat `0` allocation and `-EOPNOTSUPP` init as unsupported, not as transient allocation success. Enabled/disabled behavior must remain ABI-compatible for code built across config combinations. Release returning false in stubs means normal page-pool release paths must handle non-devmem netmem.

Test signals: Build with `CONFIG_NET_DEVMEM=y` and disabled. For disabled builds, verify callers handle `-EOPNOTSUPP`, null netmem allocation, no-op destroy, and false release. For enabled builds, test page-pool init/destroy and devmem netmem allocation/release through the real implementation.
