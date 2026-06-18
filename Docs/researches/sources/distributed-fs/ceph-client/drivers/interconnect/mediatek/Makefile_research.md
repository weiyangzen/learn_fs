# sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/Makefile

Purpose: MediaTek interconnect object mapping.

Important APIs/types/functions: builds `icc-emi.o` for `CONFIG_INTERCONNECT_MTK_DVFSRC_EMI`, `mt8183.o` for MT8183, and `mt8195.o` for MT8195.

Control flow: Make conditionals translate Kconfig into objects.

State and persistence: no runtime state; affects build products.

Dependencies/integration: consumes `mediatek/Kconfig` symbols.

Risks and test signals: `mt8196.o` is currently gated by `CONFIG_INTERCONNECT_MTK_MT8195` rather than `CONFIG_INTERCONNECT_MTK_MT8196`, which likely breaks independent MT8196 builds and adds MT8196 when selecting MT8195. Test those exact config combinations.
