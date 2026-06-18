# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/Makefile

Purpose: maps Synopsys DesignWare DRM bridge Kconfig symbols to object files.

Important APIs/types/functions: builds `dw-dp.o`, `dw-hdmi.o`, `dw-hdmi-ahb-audio.o`, `dw-hdmi-gp-audio.o`, `dw-hdmi-i2s-audio.o`, `dw-hdmi-cec.o`, `dw-hdmi-qp.o`, `dw-mipi-dsi.o`, and `dw-mipi-dsi2.o` under their corresponding `CONFIG_DRM_DW_*` symbols.

Control flow: kbuild includes exactly the objects enabled by the kernel configuration. There is no runtime behavior.

State and persistence: no state beyond build products.

Dependencies and integration: complements the local Kconfig file and lets platform-specific drivers link against exported core library symbols such as `dw_dp_bind()` and `dw_hdmi_qp_bind()`.

Risks: object/Kconfig mismatches cause missing drivers or unresolved symbols. Optional QP CEC is compiled into `dw-hdmi-qp.o` through C preprocessor guards, so there is no separate Makefile object for it.

Test signals: incremental and clean kernel builds for each symbol as built-in and module, plus link coverage for platform users.
