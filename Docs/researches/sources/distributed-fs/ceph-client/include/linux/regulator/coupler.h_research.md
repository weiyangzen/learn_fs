# sources/distributed-fs/ceph-client/include/linux/regulator/coupler.h

## Purpose

This header declares the regulator coupler API used to coordinate voltage changes across rails that must maintain a bounded voltage relationship, such as CPU/core SRAM rail pairs.

## Important APIs, Types, and Functions

`struct regulator_coupler` contains a list node and callbacks: mandatory `attach_regulator()`, optional `detach_regulator()`, and optional `balance_voltage()`. Registration and core helpers include `regulator_coupler_register()`, `regulator_check_consumers()`, `regulator_check_voltage()`, `regulator_get_voltage_rdev()`, `regulator_set_voltage_rdev()`, and `regulator_do_balance_voltage()`. Disabled regulator builds provide no-op or `-EINVAL` stubs.

## Control Flow

The core calls `attach_regulator()` when coupled regulators are created, then calls `balance_voltage()` during voltage changes while all involved regulator consumer locks are held. If no custom balancer exists, generic balancing is used. The coupler validates consumer min/max requirements and updates coupled rails in a safe order.

## State and Persistence Behavior

Coupling state is held in regulator core objects and the registered coupler list. Actual voltage state persists in hardware according to regulator driver behavior. This header does not define storage beyond the coupler object.

## Dependencies and Integration Points

It depends on errno, suspend state, and regulator core forward declarations. It integrates with `struct coupling_desc` in `driver.h`, board constraints such as `max_spread`, and suspend-state voltage programming.

## Risks

Bad balancing can violate maximum spread, brown out a rail, or deadlock if lock ordering is wrong. Attach callbacks returning the wrong code can bind unrelated regulators or leave required rails uncoupled. Disabled-config stubs hide coupling behavior.

## Test Signals

Tests should exercise attach/detach, multi-rail voltage increases/decreases, suspend-state balancing, max-spread enforcement, consumer constraint conflicts, and deadlock detection under ww-mutex locking.
