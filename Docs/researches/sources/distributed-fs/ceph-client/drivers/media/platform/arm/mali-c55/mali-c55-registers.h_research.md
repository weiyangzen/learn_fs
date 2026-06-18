# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-registers.h

Purpose: Defines Mali-C55 hardware register offsets, bit masks, field encoders, interrupt indices, capability bits, config-space sizes, metering/statistics addresses, and capture/resizer writer constants.

Important APIs/types: Provides macros for common ISP registers, ping/pong config spaces, interrupts, global parameter status capabilities, TPG, input windowing, Bayer order, metering, bypass blocks, AEXP/AWB, mesh shading, color correction, capture writers, crop/scaler/gamma, and FR/DS resizer filter banks.

Control flow and state: No executable control flow. The macros drive all MMIO and context-shadow writes in core, ISP, TPG, params, capture, stats, and resizer implementation files.

Dependencies and integration: Includes `<linux/bits.h>` for `BIT()` and `GENMASK()`. It is the central hardware ABI for the driver.

Risks: Typographical macro `MALI_c55_MESH_STRENGTH_MASK` uses lowercase `c55`; code currently references that exact spelling. `MALI_C55_REG_TEST_GEN_CH0_OFF_ON` is defined without a value and must not be used as an address. Register field comments and masks are hardware-critical and hard to validate without silicon.

Test signals: Compile coverage for every used macro, register write tracing during stream start, static analysis for unused/bad defines, and hardware tests for each enabled processing block.
