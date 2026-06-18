# sources/distributed-fs/ceph-client/drivers/power/reset/msm-poweroff.c

## Purpose
Qualcomm MSM PS_HOLD poweroff/restart driver.

## Important APIs, Types, and Functions
global mapped PS_HOLD address, poweroff and restart callbacks that clear or write PS_HOLD control.

## Control Flow
probe maps the Qualcomm control register and installs poweroff/restart hooks; shutdown drops PS_HOLD so PMIC powers down, restart requests reset behavior then drops hold.

## State and Persistence Behavior
global register pointer persists; PS_HOLD state directly controls PMIC/platform power.

## Dependencies and Integration Points
ARCH_QCOM, OF/MMIO, legacy `pm_power_off` and restart/sys-off integration.

## Risks and Edge Cases
wrong register mapping can immediately kill power; global hooks are singleton; limited confirmation after PS_HOLD drop.

## Test Signals
QCOM DT probe, shutdown and reboot on boards, register offset validation, and fallback behavior.
