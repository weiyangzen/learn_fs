# sources/distributed-fs/ceph-client/include/linux/dsa/brcm.h

## Purpose
This header provides Broadcom DSA tag helper macros for packing and unpacking a port and queue value into a single tag field.

## Important APIs, types, and functions
Macros are `BRCM_TAG_SET_PORT_QUEUE(p, q)`, `BRCM_TAG_GET_PORT(v)`, and `BRCM_TAG_GET_QUEUE(v)`.

## Control flow, state, and persistence
No runtime state exists. The macros encode the port in bits above the low byte and queue in the low byte.

## Dependencies and integration points
It is included by Broadcom Ethernet and DSA tag code. It has no include dependencies.

## Risks and test signals
There is no masking in `BRCM_TAG_SET_PORT_QUEUE()`, so out-of-range queue or port values can leak bits into adjacent fields. Tests should cover encode/decode round trips and boundary values for supported port and queue widths.
