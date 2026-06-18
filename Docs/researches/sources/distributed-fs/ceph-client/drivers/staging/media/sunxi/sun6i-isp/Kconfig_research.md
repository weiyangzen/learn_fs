# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/Kconfig

Purpose: build option for the Allwinner A31-family ISP staging driver.

Important APIs/types: `config VIDEO_SUN6I_ISP` is tristate and depends on V4L platform/video support, sunxi or compile-test, PM, common clock, and DMA. It selects media controller, V4L2 subdev API, DMA-contig and vmalloc vb2 backends, V4L2 fwnode, and regmap MMIO.

Control flow: Kconfig-only; enables building `sun6i-isp.o`.

State and persistence: build configuration state only.

Dependencies/integration: matches the driver’s use of media graph, subdevs, vb2 capture/meta queues, fwnode async discovery, regmap, PM runtime, clocks, reset, and DMA.

Risks: hardware currently matches only a subset of supported-family SoCs in code; prompt text mentions A31/A80/A83T/V3/V3s but OF table in this subset only contains `allwinner,sun8i-v3s-isp`.

Test signals: compile under `ARCH_SUNXI` and `COMPILE_TEST`, ensure selected vb2 backends are present, and verify module name/build object.
