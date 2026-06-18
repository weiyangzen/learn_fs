# `sources/distributed-fs/ceph-client/include/linux/usb/pd_ado.h`

## Purpose

`pd_ado.h` defines USB PD Alert Data Object bitfields and helper macros. ADOs carry partner alerts for battery, OCP, OTP, operating-condition changes, and related PD status events.

## Important APIs, Types, and Constants

- Macros define alert bits and masks for fixed batteries, hot-swappable batteries, battery status changes, OCP, OTP, operating condition, source input, overvoltage, and extended alerts.
- Helper macros construct ADO values and extract alert domains for TCPM policy handling.

## Control Flow and Lifetimes

When a PD partner sends an Alert message, TCPM parses the ADO using these masks and dispatches policy actions such as querying battery status or responding to protection events. The header does not implement policy.

## State and Persistence Behavior

ADO values are transient PD payloads. Persistent alert handling state lives in TCPM/Type-C policy and power-supply code.

## Dependencies and Integration Points

It integrates PD alert messages from `pd.h` with TCPM policy and Type-C power-supply/partner-management code. It depends on bit macros from kernel headers through including context.

## Risks and Edge Cases

Different alert fields overlap in a single 32-bit object, so masks and shifts must be used precisely. Unsupported extended alerts should not be treated as fatal. Battery slot bitmaps require validation against known partner battery count.

## Test Signals

Inject PD Alert messages with each alert bit set, validate battery and protection event dispatch, fuzz reserved bits, and test partners with no batteries or hot-swappable battery reports.
