<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/mvebu-soc-id.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/mvebu-soc-id.h

Purpose: Public header for MVEBU SoC ID lookup. It hides whether SoC ID support is compiled in and provides symbolic PCI device IDs for Armada 370 and XP.

Important APIs/types/functions: The API is `mvebu_get_soc_id(u32 *dev, u32 *rev)`, with an inline `-1` fallback when `CONFIG_CACHE_L2X0` is not enabled.

Control flow, state, and persistence: It stores no state itself; the C file owns cached IDs. Compile-time selection means callers must handle failure.

Dependencies and integration points: The API is `mvebu_get_soc_id(u32 *dev, u32 *rev)`, with an inline `-1` fallback when `CONFIG_CACHE_L2X0` is not enabled. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are the surprising dependency on `CONFIG_CACHE_L2X0` and broad fallback return value. Test callers with the option enabled/disabled and on platforms that do not expose SoC ID.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 51 lines, 1076 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/mvebu-soc-id.h -->
