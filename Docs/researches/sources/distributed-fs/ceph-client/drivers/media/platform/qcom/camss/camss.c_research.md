<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss.c

## Purpose
Implements the Qualcomm CAMSS platform driver: SoC resource descriptions, probe/remove, media/V4L2 registration, async sensor binding, power-domain/interconnect management, and media graph construction across CSIPHY, CSID, optional ISPIF, VFE, and video nodes.

## Important APIs, Types, And Functions
- Defines static `camss_subdev_resources` arrays for many compatibles, mapping regulators, clocks/rates, register names, interrupts, hardware ops, line counts, lite/full flags, VBIF/power-domain names, format tables, and interconnect paths.
- Core helpers include `camss_add_clock_margin()`, `camss_enable_clocks()`, `camss_disable_clocks()`, `camss_find_sensor_pad()`, `camss_get_link_freq()`, `camss_get_pixel_clock()`, `camss_pm_domain_on/off()`, `camss_reg_update()`, and `camss_buf_done()`.
- Driver flow is in `camss_probe()`, `camss_remove()`, notifier callbacks, runtime PM callbacks, and the `qcom_camss_driver` platform driver.

## Control Flow
Probe allocates the CAMSS object and per-block arrays from matched resource data, gets interconnect paths, configures top-level power domains, initializes CSIPHY/VFE/CSID/ISPIF subdevices, sets the DMA mask, registers media and V4L2 devices, initializes the async notifier, parses fwnode endpoints, registers internal entities, creates internal media links, registers the media device, and waits for external sensor subdevs. Bound sensors attach CSI lane config to the target CSIPHY; notifier completion links sensor source pads to CSIPHY sinks and registers subdev nodes. Runtime resume programs interconnect bandwidth; suspend clears it. Remove unregisters notifier and entities, deletes media/V4L2 state when video references are gone, and detaches power domains.

## State And Persistence
State is the bound `struct camss`: resource pointer, arrays of subdevices, media/v4l2 devices, notifier, device pointer, top-level and VFE power-domain links, interconnect paths, CSID wrapper base, and a video-node reference count. No persistent storage is written.

## Dependencies And Integration Points
Depends on platform OF matching, fwnode graph endpoints, V4L2 async/media-controller frameworks, runtime PM, generic PM domains, interconnect framework, DMA masks, and all CAMSS block-specific modules. Device-tree compatible strings select exact resource tables.

## Risks And Edge Cases
Resource tables are large and tightly coupled to DT names; any clock/reg/interrupt/power-domain mismatch breaks probe. Some platforms use legacy power-domain index assumptions. Async endpoint parsing only supports CSI2 D-PHY, rejecting C-PHY. Link creation builds broad crossbar-style links, so wrong pad counts or line counts can create invalid graphs. `camss_remove()` defers full delete while video references remain, making ref-count correctness important.

## Test Signals
Probe should succeed for each compatible with matching DT, media graph topology should show expected sensors and internal links, runtime PM should set/clear interconnect bandwidth, stream tests should exercise `camss_reg_update()`/`camss_buf_done()` routing, and remove/unbind should clean up without leaked entities or power-domain links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss.c -->
