# sources/distributed-fs/ceph-client/include/linux/regulator/arizona-micsupp.h

## Purpose

This header defines platform data for the Arizona microphone-supply regulator.

## Important APIs, Types, and Functions

`struct arizona_micsupp_pdata` contains `const struct regulator_init_data *init_data` describing regulator constraints and consumers for the microphone supply.

## Control Flow

The Arizona parent driver supplies this structure to the micsupp regulator child, which registers the regulator with the core using the init data.

## State and Persistence Behavior

The header has no runtime state. Hardware enable/voltage behavior belongs to the regulator driver and codec hardware.

## Dependencies and Integration Points

It forward-declares `regulator_init_data` and integrates with Arizona MFD platform data.

## Risks

Incorrect constraints can affect microphone bias/supply sequencing and audio capture reliability.

## Test Signals

Probe tests should verify micsupp constraints, enable behavior, and consumer supply lookup on boards using platform data.
