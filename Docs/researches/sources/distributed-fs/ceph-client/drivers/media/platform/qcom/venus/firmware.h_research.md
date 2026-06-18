# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/firmware.h

## Purpose
`firmware.h` declares the Venus firmware lifecycle and hardware-state APIs used by core and PM code.

## Important APIs
- `venus_firmware_init()` / `venus_firmware_deinit()` for firmware child device and IOMMU setup.
- `venus_firmware_check()` and `venus_firmware_cfg()` for version validation and platform-specific firmware register configuration.
- `venus_boot()` / `venus_shutdown()` for loading/authenticating/resetting and stopping firmware.
- `venus_set_hw_state()` plus inline `venus_set_hw_state_suspend()` and `venus_set_hw_state_resume()` wrappers.

## Control Flow And Integration
`core.c` uses the lifecycle sequence during probe, recovery, remove, and shutdown. PM helpers can use the suspend/resume wrappers to put firmware CPU state into reset or release it depending on secure/non-secure mode.

## State And Persistence
The header owns no state. Functions mutate `struct venus_core` firmware fields and hardware registers in `firmware.c`.

## Dependencies
Forward use of `struct venus_core` is expected through including translation units. The header also references `bool`.

## Risks
- The parameter name in `venus_set_hw_state(struct venus_core *core, bool suspend)` is semantically opposite the implementation name `resume`; callers should use the inline wrappers to avoid confusion.
- Calling boot/shutdown outside the expected runtime PM and HFI ordering can leave firmware state inconsistent.

## Test Signals
Build coverage validates exported signatures. Runtime tests should cover secure boot, non-secure child firmware node boot, suspend/resume wrappers, and probe unwind after boot failures.
