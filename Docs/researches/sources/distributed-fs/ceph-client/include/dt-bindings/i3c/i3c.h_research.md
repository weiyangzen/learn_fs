# sources/distributed-fs/ceph-client/include/dt-bindings/i3c/i3c.h

## Purpose
defines I3C Devicetree dynamic-address assignment flags.

## Important APIs, Types, and Functions
The visible API is `I2C_FM`, `I2C_FM_PLUS`, `I2C_FILTER`, `I2C_NO_FILTER_HIGH_FREQUENCY`, `I2C_NO_FILTER_LOW_FREQUENCY`, an address-slot flag used by I3C controller bindings when describing devices that need dynamic address assignment policy.

## Control Flow
There is no runtime flow in the header. The flag is compiled into DTB data and interpreted by I3C core/controller code while building the bus device list.

## State, Persistence, and Dependencies
No state is stored; the ABI is the flag bit value encoded in Devicetree. Integration is with I3C bus bindings and controller/client registration paths.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The risk is conflicting flag bits or missing controller-side validation, which can cause wrong dynamic-address handling.

## Test Signals
DTS compile tests and controller probe tests should verify dynamic-address assignment behavior with and without the flag.
