# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/version.h

## Purpose
Defines HRT interface version macros for AtomISP support code.

## Important APIs, Types, and Functions
Macros are `HRT_VERSION_MAJOR 1`, `HRT_VERSION_MINOR 4`, and `HRT_VERSION 1_4`.

## Control Flow
No execution.

## State and Persistence Behavior
Static version metadata only.

## Dependencies and Integration Points
No includes. Consumers can use it for compile-time compatibility checks or reporting.

## Risks
`HRT_VERSION 1_4` is token-style rather than a numeric expression, so consumers must use it consistently.

## Test Signals
Compile coverage where version macros are referenced.
