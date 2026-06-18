# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/media-dev.c

## Purpose
Implements the top-level Samsung S5P/Exynos FIMC media device, responsible for discovering sensors and platform subdevices, constructing media links, managing pipeline power/stream order, exposing camera clocks, and registering the media device.

## Important APIs, Types, and Functions
Important functions include `fimc_pipeline_prepare()`, `fimc_pipeline_s_power()`, `__fimc_pipeline_open()`, `__fimc_pipeline_s_stream()`, platform entity registration helpers, sensor DT parsing, link creation helpers, link-notify pipeline modification, clock-provider registration, async notifier callbacks, `fimc_md_probe()`, and module init/exit.

## Control Flow
Probe populates child platform devices, initializes media/v4l2 devices, obtains clocks, registers FIMC/FIMC-LITE/CSIS/FIMC-IS entities, parses sensor endpoints, exposes the subdev API mode sysfs attribute, registers camera-clock providers, and waits for async sensor binding. Completion creates sensor-to-CSIS/FIMC/FIMC-LITE/ISP links, registers subdev nodes, and registers the media device. Opening a video node prepares the active graph, powers subdevs in ordered sequences, and streaming calls `.s_stream` in a separate order with rollback on failure.

## State and Persistence
`struct fimc_md` stores arrays of registered platform entities and sensors, async connections, camera/writeback clocks, pipeline objects, media/v4l2 devices, user-subdev API mode, and graph walk state. State is runtime-only; sysfs toggles affect current in-memory pipeline configuration behavior.

## Dependencies and Integration Points
Depends on OF graph parsing, v4l2-async, media-controller graph/link APIs, clk provider APIs, runtime PM, FIMC/FIMC-LITE/FIMC-IS/CSIS subdrivers, and Exynos pipeline operations.

## Risks and Edge Cases
`fimc_md_create_links()` calls `__fimc_md_create_flite_source_links()` unconditionally, but that helper dereferences `fmd->fimc_is` when FIMC-LITE instances exist; non-ISP configurations with FIMC-LITE need coverage. `subdev_notifier_bound()` increments `num_sensors` even though the same field was used as a parse count and reset before notifier registration, making count semantics phase-dependent. Link-notify rollback is complex and can leave power use-counts wrong if subdev callbacks return mixed errors.

## Test Signals
Validate DTs with parallel sensors, CSI sensors, FIMC-IS sensors, no sensors, no ISP, and multiple FIMC/FIMC-LITE entities; toggle `subdev_conf_mode`; exercise link changes while video nodes are open; and verify power/stream order and clock-provider PM balancing.
