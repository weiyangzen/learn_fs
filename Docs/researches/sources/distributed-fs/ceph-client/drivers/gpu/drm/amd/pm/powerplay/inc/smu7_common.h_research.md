# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_common.h

## Purpose
`smu7_common.h` is a small shared constants header for SMU7-family power management. It centralizes feature bit positions and masks used by the host driver and firmware-facing code to enable DPM, thermal, voltage, media, PCIe, display, and memory power-management features.

## Important APIs, Types, And Constants
- Defines feature bit positions such as `SMU7_SCLK_DPM_CONFIG_ID`, `SMU7_MCLK_DPM_CONFIG_ID`, `SMU7_UVD_DPM_CONFIG_ID`, `SMU7_VCE_DPM_CONFIG_ID`, `SMU7_ACP_DPM_CONFIG_ID`, `SMU7_SAMU_DPM_CONFIG_ID`, `SMU7_PCIEGEN_DPM_CONFIG_ID`, and other SMU7 feature selectors.
- Provides matching `SMU7_*_CONFIG_MASK` macros via bit shifts.
- The header is guarded by `SMU7_COMMON_H`.

## Control Flow And Data Flow
There is no executable control flow. Driver policy code uses these masks to compose feature-enable fields sent to SMU soft registers or SMC messages. Firmware reads the resulting bitmask to determine which controllers should run.

## State And Persistence
The header defines constants only. It has no storage, persistence, or runtime ownership.

## Dependencies And Integration Points
- Shared by SMU7-family implementation files that need feature-enable bitmasks.
- Integrates indirectly with `FeatureEnables` fields in SMU soft registers and DPM table programming.

## Risks
- Bit position changes are ABI changes for every firmware consumer.
- Duplicated mask names in generation-specific headers can diverge; consumers should include the intended generation header consistently.

## Test Signals
- Compile coverage for all SMU7-family users.
- Runtime feature enablement should match requested policy: enabling one mask must not toggle unrelated DPM blocks.
