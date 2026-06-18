# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/constants.h

## Purpose

Centralizes compile-time default constants for MVM power save, U-APSD, Bluetooth coexistence, quota, rate scaling, FTM/ToF, scanning, TWT, AP behavior, passive scan timing, beacon interval limits, and automatic EML.

## Important APIs, Types, and Functions

No functions or types. Major groups include power-save timeouts/windows, U-APSD queues and thresholds, BT coexistence module toggles/MPLUT/reduced-power thresholds, quota and TCM thresholds, rate-scaling retry/success/failure/aggregation knobs, FTM algorithms and timing, EBS/TWT/AP FILS/6 GHz scan defaults, minimum beacon interval, and EML enable default.

## Control Flow

No runtime flow. Included constants shape command construction and policy decisions elsewhere.

## State and Persistence Behavior

Constants are immutable at runtime unless other code layers debugfs or module-parameter overrides. They influence behavior across association, coexistence, power save, scans, rate control, FTM, and suspend/resume.

## Dependencies and Integration Points

Includes `linux/ieee80211.h` and `fw-api.h` for values used in macro expressions. Consumed broadly by MVM power, coexistence, scan, FTM, and rate-scaling paths.

## Risks

Unit confusion is the main risk: values mix microseconds, milliseconds, TU, seconds, percentages, packet counts, and booleans. Small threshold changes can alter power, latency, throughput, and coexistence behavior.

## Test Signals

Policy changes require power-save, WoWLAN, BT coexistence, throughput/rate-control, FTM, scan dwell, 6 GHz passive scan, beacon interval, and EML validation.
