## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dcr.h

Purpose: provides the public architecture DCR mapping/read/write facade when `CONFIG_PPC_DCR` is enabled.

Important APIs/types/functions: aliases `dcr_host_t` to `dcr_host_native_t`, maps `DCR_MAP_OK`, `dcr_map()`, `dcr_unmap()`, `dcr_read()`, and `dcr_write()` to native helpers, and declares `dcr_resource_start()` and `dcr_resource_len()` for device-tree resources.

Control flow: wrapper macros delegate to native DCR implementation. Device-tree helpers parse DCR resource ranges elsewhere.

State and persistence: no local state. It exposes hardware DCR register access and resource metadata.

Dependencies and integration: depends on `dcr-native.h` and `struct device_node`. Used by drivers that should not care whether DCR access is native or abstracted.

Risks and test signals: wrapper availability is config-gated; callers must not assume DCR APIs exist without `CONFIG_PPC_DCR`. Test signals include DCR device probe, device-tree DCR resource parsing, and builds with DCR disabled.
