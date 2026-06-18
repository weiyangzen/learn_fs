# sources/distributed-fs/ceph-client/include/media/mipi-csi2.h

## Purpose
Defines MIPI CSI-2 data type constants for media bus users.

## Important APIs, Types, and Functions
The header enumerates CSI-2 short packet types for frame/line start/end and generic short packets, and long packet types for null/blanking/embedded data, generic long packets, YUV420/422 variants, RGB444/555/565/666/888, RAW6/7/8/10/12/14/16/20/24/28, and user-defined types.

## Control Flow
No runtime flow. CSI-2 receiver/transmitter drivers use the constants when validating media bus formats and packet data types.

## State and Persistence Behavior
No state. Constants mirror CSI-2 protocol values.

## Dependencies and Integration Points
Integrates V4L2 media bus format negotiation and MIPI CSI-2 hardware drivers.

## Risks
Protocol constant drift breaks packet filtering or format negotiation. Generic and user-defined macros rely on callers passing values in documented ranges.

## Test Signals
CSI-2 format negotiation, RAW/YUV/RGB packet capture, embedded data routing, and compile checks for all users.
