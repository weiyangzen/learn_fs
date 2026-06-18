# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_pwr.h

## Purpose
Declares the Panthor power-control public interface. It is the boundary used by device bring-up, reset, runtime PM, and firmware/power sequencing code.

## Important APIs, Types, and Functions
The header forward-declares `struct panthor_device` and exports `panthor_pwr_init()`, `panthor_pwr_unplug()`, `panthor_pwr_reset_soft()`, `panthor_pwr_l2_power_off()`, `panthor_pwr_l2_power_on()`, `panthor_pwr_suspend()`, and `panthor_pwr_resume()`.

## Control Flow
Device code initializes the block if present, uses soft reset during reset flows, powers L2 on before delegating shader/tiler domains to firmware, powers L2 off after retracting dependent domains, masks IRQs on suspend/unplug, and resumes IRQ handling on resume.

## State and Persistence
The header stores no state. The implementation owns `ptdev->pwr`, pending power requests, and IRQ state. Callers only receive integer success/failure for operations that can block or timeout.

## Dependencies and Integration Points
Integrates with `panthor_device`, runtime reset sequencing, and power management. The API is intentionally narrow so non-PWR_CONTROL hardware can be represented by no-op init/suspend paths in the implementation.

## Risks and Edge Cases
Callers must tolerate `panthor_pwr_init()` returning success without creating `ptdev->pwr` on unsupported hardware. L2 power operations must be ordered relative to MCU/firmware state to avoid powering down delegated domains incorrectly.

## Test Signals
Compile coverage plus reset and runtime PM tests are the key signals. On non-PWR hardware, init/suspend/resume/unplug should be harmless; on PWR hardware, soft reset and L2 on/off should return meaningful errors on disallowed transitions.
