# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/Kconfig

Purpose: build configuration for Lantiq/Intel/MaxLinear GSWIP DSA drivers and their common module.

Important APIs/types/functions: defines hidden `NET_DSA_LANTIQ_COMMON`, visible `NET_DSA_LANTIQ_GSWIP`, and visible `NET_DSA_MXL_GSW1XX`. The visible options select their DSA tag protocols and common code; MaxLinear also selects `PHY_COMMON_PROPS`.

Control flow: no runtime flow. Kconfig choices determine which objects and taggers are built.

State and persistence: no runtime state; persistent effect is kernel configuration.

Dependencies and integration: SoC GSWIP depends on `HAS_IOMEM`; both visible drivers select `NET_DSA_LANTIQ_COMMON`. Taggers are `NET_DSA_TAG_GSWIP` and `NET_DSA_TAG_MXL_GSW1XX`.

Risks and test signals: dependency or tagger omissions cause build/link/runtime tag protocol failures. Test modular and built-in builds for both visible drivers.
