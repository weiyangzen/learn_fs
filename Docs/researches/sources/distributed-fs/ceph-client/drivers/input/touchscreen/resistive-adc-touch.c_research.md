<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/resistive-adc-touch.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/resistive-adc-touch.c

## Purpose
`resistive-adc-touch.c` is a generic platform driver for resistive touchscreens whose samples arrive through IIO channels rather than a dedicated touchscreen controller driver. It maps named ADC channels from firmware properties, converts raw X/Y and optional pressure data into input events, and starts/stops the IIO callback buffer on input open/close.

## Important APIs, Types, And Functions
`enum grts_ch_type` defines logical channels: X, Y, direct pressure, Z1, and Z2. `struct grts_state` stores X-plate resistance, pressure threshold, channel list/callback, input device, touchscreen transform properties, and a logical-to-IIO channel map. `grts_map_channel()` resolves entries in `io-channel-names`; `grts_get_properties()` validates required X/Y, optional direct pressure, or optional Z1/Z2 pressure calculation with `touchscreen-x-plate-ohms`. `grts_cb()` is the IIO callback that reads the sample array and reports input state. `grts_open()` and `grts_close()` start and stop `iio_channel_start_all_cb()` / `iio_channel_stop_all_cb()`.

## Control Flow
Probe obtains all IIO channels, requires `io-channel-names`, parses channel mapping and pressure configuration, allocates a `BUS_HOST` input device, sets ABS_X/ABS_Y and optional ABS_PRESSURE limits, parses touchscreen axis properties, registers the input device, then creates an all-channel IIO callback buffer. When userspace opens the input node, the callback buffer begins streaming. Each callback extracts X/Y, computes direct pressure or resistive pressure from Z1/Z2 and X-plate resistance, emits release if X/Y are zero or pressure is below threshold, otherwise reports transformed position, pressure, `BTN_TOUCH`, and sync.

## State And Persistence
All state is runtime-only. The driver persists no calibration or settings; thresholds and channel topology come from device properties at probe. The IIO callback object is devres-cleaned through `grts_disable()`.

## Dependencies And Integration Points
It integrates the IIO consumer callback API, generic device properties/OF, input core, and touchscreen property parsing. It expects channel ordering and names to match the sampled buffer layout.

## Risks
The code supports at most four channels and uses `GRTS_MAX_CHANNELS` as the sentinel. A misordered or incomplete `io-channel-names` property silently changes pressure behavior. Z1/Z2 pressure math avoids division by zero but depends on realistic plate resistance and sample ranges. Direct release detection treats `(x == 0 && y == 0)` as no touch, which can conflict with panels that can legitimately report origin.

## Test Signals
Validate DT bindings for required names, confirm IIO buffer starts only while the input device is open, observe releases below `touchscreen-min-pressure`, test Z1/Z2 pressure against known loads, and use evtest to confirm axis transforms and `BTN_TOUCH` transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/resistive-adc-touch.c -->
