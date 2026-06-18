# sources/distributed-fs/ceph-client/include/media/drv-intf/renesas-ceu.h

Purpose: Platform-data interface for the Renesas CEU capture driver.

Important APIs/types/functions: `CEU_MAX_SUBDEVS` limits platform subdevices to two. `ceu_async_subdev` stores bus flags, bus width/shift, I2C adapter ID, and I2C address. `ceu_platform_data` carries the subdevice count and fixed subdevice array.

Control flow: Board/platform code fills CEU subdevice wiring; the CEU driver uses it to create async subdevice matches and configure parallel bus geometry.

State and persistence: Static platform data only; live capture and async state are in the CEU driver.

Dependencies and integration: Integrates legacy platform data with V4L2 async sensor discovery for Renesas CEU.

Risks and test signals: Risks are exceeding `CEU_MAX_SUBDEVS`, wrong bus shift/width, or bad I2C addresses. Test probe with zero/one/two subdevices, async bind/unbind, and capture on each declared bus layout.
