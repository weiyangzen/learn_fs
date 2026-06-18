<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/media/video-interfaces.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/media/video-interfaces.h

## Purpose
This common media binding header defines video bus type constants, CSI-2 C-PHY line order encodings, and parallel pixel-clock sample edge constants.

## Important APIs, types, and functions
It exports `MEDIA_BUS_TYPE_CSI2_CPHY`, `CSI1`, `CCP2`, `CSI2_DPHY`, `PARALLEL`, `BT656`, C-PHY line order constants `MEDIA_BUS_CSI2_CPHY_LINE_ORDER_ABC` through `CBA`, and pixel clock sample constants `MEDIA_PCLK_SAMPLE_FALLING_EDGE`, `RISING_EDGE`, and `DUAL_EDGE`.

## Control flow
Media endpoint DTS nodes include the header and use these constants in bus-type, lane-order, and pclk properties. V4L2 fwnode parsers and media drivers convert the numeric values into endpoint bus configuration.

## State and persistence
The header has no state. Values persist in DTBs and control runtime media bus setup.

## Dependencies and integration points
It integrates with generic video-interface schemas, V4L2 fwnode endpoint parsing, CSI-2 C-PHY/D-PHY receivers, parallel/BT.656 capture drivers, and sensor/display bridge endpoints.

## Risks and test signals
Risks include mismatched bus type between sensor and receiver, wrong C-PHY trio order, and incorrect pixel sampling edge causing unstable images. Test signals include `dtbs_check`, media graph validation, endpoint parser logs, sensor stream-on, and captured frame integrity under the configured bus mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/media/video-interfaces.h -->
