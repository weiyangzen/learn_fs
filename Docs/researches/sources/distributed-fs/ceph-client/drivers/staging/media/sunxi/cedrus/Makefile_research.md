# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/Makefile

Purpose: builds the Cedrus driver objects into `sunxi-cedrus.o`.

Important APIs/types: `obj-$(CONFIG_VIDEO_SUNXI_CEDRUS) += sunxi-cedrus.o`; the composite object includes core, video, hardware, decode dispatcher, and MPEG2/H264/H265/VP8 codec files.

Control flow: kbuild links all listed codec implementations into a single module/built-in object.

State and persistence: build graph only.

Dependencies/integration: object list mirrors extern decoder ops declared in `cedrus.h`; removing a codec object without changing controls/formats would break symbols.

Risks: codec capabilities are runtime gated by SoC variant, not by separate build options, so all listed codec code is always compiled when Cedrus is enabled.

Test signals: compile with `CONFIG_VIDEO_SUNXI_CEDRUS=m` and `=y`; inspect `modinfo sunxi-cedrus` and symbol resolution for all `cedrus_dec_ops_*`.
