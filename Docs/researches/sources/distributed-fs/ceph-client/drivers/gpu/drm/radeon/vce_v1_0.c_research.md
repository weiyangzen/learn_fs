# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/vce_v1_0.c

## Purpose

`vce_v1_0.c` implements first-generation Radeon Video Coding Engine support: firmware signature preparation, BO sizing, memory-controller/cache setup, firmware authentication polling, clock-gating control, dual VCE ring start, ring pointer accessors, and init-time ring tests.

## Important APIs, Types, and Functions

- `struct vce_v1_0_fw_signature` describes the signed firmware metadata, chip-id entries, nonces, signatures, and key select value.
- Ring callbacks `vce_v1_0_get_rptr()`, `vce_v1_0_get_wptr()`, and `vce_v1_0_set_wptr()` select ring 1 or ring 2 registers based on `ring->idx`.
- `vce_v1_0_enable_mgcg()` and `vce_v1_0_init_cg()` program VCE/UENC clock-gating registers.
- `vce_v1_0_load_fw()` selects a signature by chip ID, writes nonce, firmware payload, signature, and `rdev->vce.keyselect` into the VCE BO image.
- `vce_v1_0_bo_size()` returns firmware plus stack plus per-handle data size.
- `vce_v1_0_resume()` programs LMI/cache registers, scratch max-handle count, firmware keyselect, polls firmware status for done/pass/not-busy, then initializes clock gating.
- `vce_v1_0_start()` sets ring base/size/pointers for both VCE rings, resets and boots ECPU/FME blocks, polls `VCE_STATUS`, and clears the busy flag.
- `vce_v1_0_init()` starts VCE, marks both rings ready, and runs ring tests.

## Control Flow

Firmware load runs before resume and transforms the signed firmware blob into the BO layout expected by the VCE security engine. Resume disables/initializes gating, configures LMI and three cache regions at fixed sizes after a 256-byte header, writes keyselect, waits for firmware authentication to complete/pass, waits for the busy bit to clear, and initializes clock gating.

Start configures both ring buffers, enables VCPU clock, asserts/deasserts soft resets, waits for status bit 2 with retry resets, clears busy, and returns success only when the engine responds. Init then validates both rings independently and leaves their `ready` flags true only after successful tests.

## State and Persistence Behavior

Persistent driver state includes `rdev->vce.keyselect`, VCE BO GPU address, ring `wptr/ready`, and firmware object data. Hardware state includes LMI/cache range registers, firmware authentication state, clock-gating registers, status bits, reset bits, ring base/size/pointer registers, and scratch max-handle count.

## Dependencies and Integration Points

- Uses Radeon firmware, ring, ASIC family, register, and clock-gating infrastructure.
- Register definitions come from `sid.h`; ring indexes use Trinity/Southern Islands VCE ring constants.
- `trinity_dpm.c` calls `vce_v1_0_enable_mgcg()` around VCE clock changes.

## Risks and Edge Cases

- `vce_v1_0_load_fw()` trusts signature header fields enough to copy `rdev->vce_fw->size - sizeof(*sign)` into the target buffer; malformed firmware could exceed fixed BO layout despite `bo_size()` warning only checking total firmware size.
- Signature table iteration uses firmware-provided `num` without bounding it to the fixed `val[8]` array.
- `vce_v1_0_bo_size()` uses `WARN_ON()` but still returns a size even if firmware is larger than the fixed VCE firmware area.
- Start failure returns `-1` rather than a specific errno.
- Long polling delays can make failure paths slow.

## Test Signals

- Firmware-load tests should cover each supported family chip ID and malformed signature counts/lengths.
- Resume tests should validate firmware status done/pass/busy handling and timeout/error returns.
- Ring tests should confirm both VCE rings are programmed and tested independently.
- Clock-gating tests should verify registers change only when `RADEON_CG_SUPPORT_VCE_MGCG` permits enable.
