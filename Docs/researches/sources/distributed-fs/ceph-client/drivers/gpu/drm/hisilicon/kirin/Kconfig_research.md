# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/Kconfig

Purpose: declares the `DRM_HISI_KIRIN` build option for Hisilicon Kirin/Hi6220 DRM support.

Important APIs/types: the config is a tristate requiring DRM, OF, and ARM64 or compile-test. It selects DRM client selection, KMS helper, GEM DMA helper, and MIPI DSI support.

Control flow: Kconfig selection controls whether `kirin-drm` and `dw_drm_dsi` are built by the directory Makefile.

State and persistence: no runtime state. It influences kernel build configuration.

Dependencies and integration points: integrates Kirin DRM with the DRM core, OF graph/component model, DMA GEM backing, and MIPI DSI host support.

Risks: missing selected dependencies would break link or runtime probe. The help text targets Hi6220 and may not cover broader Kirin variants.

Test signals: allmodconfig/allyesconfig build, module build as `M`, and OF-enabled platform probe.
