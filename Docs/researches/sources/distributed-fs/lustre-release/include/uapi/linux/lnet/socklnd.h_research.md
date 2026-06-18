# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/socklnd.h

## Purpose
This small UAPI header defines shared socket LND connection type constants used by the socknal implementation and utilities.

## Important APIs, Types, And Functions
Constants are `SOCKLND_CONN_NONE`, `SOCKLND_CONN_ANY`, `SOCKLND_CONN_CONTROL`, `SOCKLND_CONN_BULK_IN`, `SOCKLND_CONN_BULK_OUT`, `SOCKLND_CONN_NTYPES`, and alias `SOCKLND_CONN_ACK`.

## Control Flow
There is no executable control flow. Consumers use these values to classify socket connections by control traffic, inbound bulk, outbound bulk, or wildcard/none selection.

## State, Persistence, And Dependencies
No state is stored. The constants are ABI shared between kernel and tools, so their numeric values are persistent.

## Integration Points
The header is included by socklnd internals and administrative/user utilities that display or configure socklnd connection classes.

## Risks
Renumbering values breaks tool/kernel interpretation. The alias `SOCKLND_CONN_ACK` maps to bulk-in, so code that treats ACK as a separate connection type would be wrong.

## Test Signals
Test signals are compile coverage in socklnd and utilities, connection-class display/configuration round trips, and assertions that `SOCKLND_CONN_NTYPES` stays aligned with implemented connection arrays.
