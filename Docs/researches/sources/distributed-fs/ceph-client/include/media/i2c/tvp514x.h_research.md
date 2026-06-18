# sources/distributed-fs/ceph-client/include/media/i2c/tvp514x.h

## Purpose
Defines input/output selectors and platform data for TI TVP514x analog video decoders.

## Important APIs, Types, and Functions
Macros define module name, BT.656 clock, and NTSC/PAL active dimensions. `enum tvp514x_input` lists composite/S-Video/component and test inputs. `enum tvp514x_output` lists output interface modes. `struct tvp514x_platform_data` supplies clock and platform-specific routing.

## Control Flow
The driver programs input mux, output bus mode, and timing according to platform data and runtime routing.

## State and Persistence Behavior
Static board data and runtime routing persist in chip registers. Standard-specific active dimensions inform format negotiation.

## Dependencies and Integration Points
Used by V4L2 bridge drivers with TVP514x decoders on BT.656-style capture buses.

## Risks
Wrong input/output constants produce no video or invalid embedded sync. Clock mismatch breaks BT.656 capture timing.

## Test Signals
Composite/S-Video/component routing, NTSC/PAL format dimensions, BT.656 sync capture, and output mode switching.
