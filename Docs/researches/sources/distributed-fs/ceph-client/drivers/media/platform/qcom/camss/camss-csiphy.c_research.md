
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy.c

## Purpose
Provides the common CSIPHY V4L2 subdevice implementation: supported media-bus formats, resource initialization, runtime power, clock-rate selection from sensor link frequency, stream enable/disable, pad format handling, media link setup, and entity registration.

## Important APIs, Types, and Functions
Exports `csiphy_formats_8x16`, `csiphy_formats_8x96`, `csiphy_formats_sdm845`, `msm_csiphy_subdev_init()`, `msm_csiphy_register_entity()`, and `msm_csiphy_unregister_entity()`. Core helpers include `csiphy_set_clock_rates()`, `csiphy_set_power()`, `csiphy_stream_on()`, `csiphy_try_format()`, and pad ops for enum/get/set format. Hardware-specific behavior is dispatched through `struct csiphy_hw_ops`.

## Control Flow
Probe-time init maps MMIO and optional clock mux, requests an IRQ with `IRQF_NO_AUTOEN`, builds clock/rate arrays, identifies clocks whose rates are set dynamically, and gets regulators. Power-on resumes runtime PM, enables regulators, computes timer clock rate from sink format bpp and CSI-2 lane count, enables clocks and IRQ, resets hardware, and logs HW version. Stream-on computes link frequency, programs the CSID clock mux when present, then calls hardware `lanes_enable()`. Media link setup stores the downstream CSID id and prevents multiple enabled source links.

## State and Persistence
`struct csiphy_device` stores current pad formats, CSI-2 lane config, selected CSID, power resources, clocks, and hardware ops. State is in memory and registers only; format state is active or TRY state via V4L2 subdev state.

## Dependencies and Integration Points
Integrates sensors to CSID blocks in the media graph, uses `camss_get_link_freq()`, PM runtime, regulators, clocks, platform resources, and V4L2/media APIs. It depends on hardware files such as `camss-csiphy-3ph-1-0.c`.

## Risks and Test Signals
`csiphy_try_format()` references `MSM_CSID_PAD_SINK` while copying the CSIPHY sink format; this is currently equivalent to zero but brittle. Clock-rate selection assumes sorted frequency tables and can reject high pixel clocks. Test via media graph link exclusivity, format propagation sink-to-source, runtime PM unwind on failures, timer clock rate programming, mux selection for combo mode, and stream-on/off with real sensors.
