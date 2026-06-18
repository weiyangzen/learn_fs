# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/edp.xml

## Purpose
This XML describes MSM embedded DisplayPort controller, AUX, interrupt, PHY, and 28nm eDP PLL registers. It covers mainlink enable/reset, link training state, stream timing, M/N video values, DP MISC fields, PHY reset/status, AUX/I2C transactions, hotplug and error interrupts, and PLL programming.

## Important APIs, Types, and Functions
Generated APIs include `REG_EDP_*`, `REG_EDP_PHY_*`, and `REG_EDP_28nm_PHY_PLL_*` macros. Important enums are `edp_color_depth` and `edp_component_format`. Key registers include `MAINLINK_CTRL`, `STATE_CTRL`, `CONFIGURATION_CTRL`, `SOFTWARE_MVID`, `SOFTWARE_NVID`, total/start/sync/active timing registers, `MISC1_MISC0`, `PHY_CTRL`, `MAINLINK_READY`, `AUX_CTRL`, `INTERRUPT_REG_1`, `INTERRUPT_REG_2`, AUX data/transaction/status registers, lane power controls, PHY global controls/status, and PLL power/divider/SDM/SSC/calibration/status registers.

## Control Flow
The eDP driver configures PHY and PLL, powers lanes, enables AUX, performs link training by selecting training patterns and polling readiness, programs M/N and stream timing from the DRM mode, sets color/MISC fields, and finally sends video over the mainlink. AUX control registers drive DPCD/EDID I2C-over-AUX transactions, while interrupt registers expose HPD, AUX completion, timeout/NACK/defer, PLL unlock, ready-for-video, frame-end, and CRC events.

## State and Persistence Behavior
Hardware state includes lane power, PHY/PLL settings, training pattern state, link configuration, video timing, M/N values, AUX transaction state, HPD/interrupt masks, and stream enable. It is volatile across display powerdown and suspend, so link training and timing programming are replayed on resume or modeset.

## Dependencies and Integration Points
This map integrates with DRM DP helpers, eDP bridge/connector code, AUX transfer code, EDID/DPCD reads, clock/PHY/regulator setup, link training, and display timing setup. The PLL subdomain resembles 28nm DSI PLL style controls but is eDP-specific in integration.

## Risks
Wrong training pattern or readiness bits can make link training hang. Interrupt registers use status/ack/enable triplets, so ack polarity errors can lose HPD/AUX events. The `INTERRUPT_REG_2` field positions include suspicious overlap around frame-end and CRC bits, which should be verified against hardware behavior before adding new consumers. Incorrect MISC/color depth encoding can produce wrong colors or sink rejection.

## Test Signals
Useful tests include AUX EDID/DPCD reads, link training across lane counts/rates, HPD plug/unplug events, suspend/resume, CRC/frame-end interrupt behavior, PLL unlock handling, modes with different bpc values, and generated-header compilation.
