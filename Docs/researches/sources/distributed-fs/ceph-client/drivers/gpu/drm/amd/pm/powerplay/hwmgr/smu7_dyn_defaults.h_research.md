# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_dyn_defaults.h

## Purpose

This header defines default dynamic-power-management constants for SMU7 hardware manager behavior. These constants seed thresholds, hysteresis, display-watermark behavior, activity targets, and low-power defaults when firmware tables or runtime policy do not supply all values.

## Important APIs, Types, and Functions

There are no functions or types. The file defines default values for voting-rights clients, thermal protection counter, static-screen threshold, GFX idle clock-stop threshold, reference divider, ULV voltage-change delay, CG ULV parameter/control words, and target activity percentages for general, MCLK, and SCLK DPM policy.

## Control Flow and State

The file has no runtime control flow. Its constants become initial state when included by SMU7 hwmgr initialization code.

## Dependencies and Integration

It is a local configuration header for SMU7 hwmgr modules. The values integrate with SMU7 dynamic-state defaults and activity-based DPM policy setup.

## Risks and Test Signals

Hardcoded defaults can be wrong for board-specific tuning or firmware revisions. Because constants are compile-time, regressions surface as changed DPM behavior rather than direct failures. Test signals include stable idle clocks, appropriate activity-based SCLK/MCLK scaling, thermal protection behavior, and power consumption comparisons across SMU7 ASICs.
