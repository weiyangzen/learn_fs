# sources/distributed-fs/ceph-client/include/linux/regulator/machine.h

## Purpose

`machine.h` declares board/platform-side regulator constraints and initial data. It tells regulator providers and consumers which voltage/current/mode/status operations are allowed on a specific machine, what ranges are safe, how rails behave in suspend, and how supplies map to consumers.

## Important APIs, Types, and Functions

Operation flags include `REGULATOR_CHANGE_VOLTAGE`, `CURRENT`, `MODE`, `STATUS`, `DRMS`, and `BYPASS`. Suspend enable policy values are `DO_NOTHING_IN_SUSPEND`, `DISABLE_IN_SUSPEND`, and `ENABLE_IN_SUSPEND`. `enum regulator_active_discharge` controls initial discharge policy.

`struct regulator_state` describes suspend voltage/range/mode and enable policy. `struct notification_limit` stores protection/error/warn thresholds. `struct regulation_constraints` is the central policy object: voltage/current ranges, offsets, input voltage, power budget, system load, coupled max spread, max voltage step, valid modes/ops, suspend states, notification limits, timing, active discharge, and flags such as always-on, boot-on, apply-uV, soft-start, pull-down, system-critical, and protection/detection enables.

`struct regulator_consumer_supply` maps a supply name to a device name, with `REGULATOR_SUPPLY()` initializer. `struct regulator_init_data` combines parent supply name, constraints, consumer mappings, and opaque driver data. `regulator_has_full_constraints()` informs the core that all board constraints are known.

## Control Flow

Board data or OF parsing builds `regulator_init_data` for each rail. During provider registration, the regulator core applies constraints, may enable boot-on/always-on rails, enforce valid operation masks for consumers, set initial mode/state, and configure protection/detection limits where provider ops support them. Consumer lookup uses the supply mapping for non-DT platform data.

## State and Persistence Behavior

The structures are configuration inputs. Once applied, corresponding policy is held in regulator core constraints and can drive persistent hardware state such as voltage, mode, suspend behavior, protection thresholds, soft-start, pull-down, and active discharge.

## Dependencies and Integration Points

It depends on the consumer API and suspend state types. It integrates board files, device tree parsing, regulator providers, consumer supply lookup, suspend/resume, protection event handling, and coupled regulator balancing.

## Risks

Constraints are safety-critical. Too-wide ranges can let consumers request damaging settings; too-narrow ranges break devices. Marking always-on/boot-on incorrectly can leave rails off or prevent power saving. Invalid operation masks can allow unsupported changes. Coupled `max_spread` arrays must match coupled rail counts.

## Test Signals

Tests should validate constraint parsing/application, operation-mask enforcement, boot-on/always-on behavior, suspend-state programming, notification thresholds, power budgets, consumer mappings, and full-constraints behavior.
