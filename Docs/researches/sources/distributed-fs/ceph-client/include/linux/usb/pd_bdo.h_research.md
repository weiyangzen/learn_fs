# `sources/distributed-fs/ceph-client/include/linux/usb/pd_bdo.h`

## Purpose

`pd_bdo.h` defines USB PD Battery Data Object helpers. BDOs encode battery present/capability/status information exchanged through PD battery messages.

## Important APIs, Types, and Constants

- Macros encode and decode battery status/capability fields, including invalid/unknown states where defined by the PD specification.
- The header supplies field positions and masks used by TCPM when parsing or constructing PD battery payloads.

## Control Flow and Lifetimes

PD policy code receives battery status/capability messages, decodes BDO fields, and updates partner/power-supply status. For outbound responses, policy code encodes BDOs from local battery information.

## State and Persistence Behavior

BDOs are transient 32-bit PD payload objects. Battery state persistence belongs to power-supply drivers and TCPM partner state.

## Dependencies and Integration Points

It integrates USB PD extended battery messages with Type-C partner management and Linux power-supply reporting.

## Risks and Edge Cases

Unknown or invalid battery values must be distinguished from real capacity/status values. Policy code must validate battery references against partner capabilities. Reserved bits should be ignored on receive and zeroed on transmit.

## Test Signals

Test battery capability/status PD exchanges, unknown-capacity handling, invalid battery indexes, reserved-bit fuzzing, and power-supply updates from decoded BDOs.
