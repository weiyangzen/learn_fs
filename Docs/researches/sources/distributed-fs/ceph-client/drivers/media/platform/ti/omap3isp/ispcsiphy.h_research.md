# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispcsiphy.h

## Purpose
`ispcsiphy.h` declares the CSI PHY state object and public acquire/release/init/cleanup API for OMAP3 ISP physical-layer users.

## Important APIs, Types, And Functions
- `struct isp_csiphy` stores the parent ISP, configuration mutex, associated CSI2 device, regulator, current owning media entity, register-resource IDs, and supported data-lane count.
- Public functions: `omap3isp_csiphy_acquire()`, `omap3isp_csiphy_release()`, `omap3isp_csiphy_init()`, and `omap3isp_csiphy_cleanup()`.

## Control Flow
The header establishes the ownership contract used by CCP2 and CSI2 stream paths: a media entity acquires the PHY before streaming and releases it when stopped. Initialization populates static hardware metadata before those paths run.

## State And Persistence
The key persistent field is `entity`, which records exclusive ownership and lets release derive the correct active pipeline/bus configuration. The mutex serializes configuration and power transitions.

## Dependencies And Integration Points
It includes `omap3isp.h` and forward-declares CSI2 and regulator types. The API connects ISP core device setup with CSI2/CCP2 receiver modules.

## Risks And Edge Cases
Consumers must pair acquire/release and must not access PHY registers outside the serialized ownership model. `num_data_lanes` is hardware-description state; incorrect initialization can allow invalid platform lane configs or reject valid ones.

## Test Signals
Build tests should cover API visibility. Runtime tests should verify acquire/release pairing, ownership tracking, and proper behavior when two media entities attempt to use the same PHY.
