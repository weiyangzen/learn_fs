# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk8xx.h

## Purpose
This binding header defines device-tree constants for Rockchip RK8xx PMIC reset behavior.

## APIs, Types, And Constants
The exported constants are `RK806_RESTART`, `RK806_RESET`, and `RK806_RESET_NOTIFY` for the `rockchip,reset-mode` property. They encode how the RK806 PMIC should participate in restart/reset flows.

## Control Flow And State
There is no code flow or state. DTS sources use these constants, and the PMIC driver interprets the resulting property at runtime.

## Dependencies And Integration
The header has no includes. Its integration point is the Rockchip RK8xx/RK806 PMIC binding and any board DTS node that sets `rockchip,reset-mode`.

## Risks And Test Signals
Risks are semantic mismatch between DTS value and driver behavior, especially because reset behavior affects reboot reliability. Build tests catch include failures; runtime tests should exercise reboot, reset, and notification paths on boards using the property.
