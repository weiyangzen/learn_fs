# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/Makefile

Purpose: builds the sun6i ISP composite driver object.

Important APIs/types: `sun6i-isp-y` includes core, proc, capture, and params objects; `obj-$(CONFIG_VIDEO_SUN6I_ISP) += sun6i-isp.o`.

Control flow: kbuild links all four implementation files into one module/built-in object.

State and persistence: build graph only.

Dependencies/integration: object list mirrors setup/cleanup calls in `sun6i_isp.c`; removing one object would break symbols.

Risks: no per-feature build toggles; params/capture/proc are always present when the ISP driver is enabled.

Test signals: module and built-in compile checks; symbol resolution for setup/cleanup functions.
