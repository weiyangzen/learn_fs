# sources/distributed-fs/ceph-client/include/dt-bindings/clock/versaclock.h

## Purpose
Defines output mode constants for the VersaClock clock generator binding. These are DT values describing electrical output type.

## Important APIs, Types, and Constants
Exports `VC5_LVPECL`, `VC5_CMOS`, `VC5_HCSL33`, `VC5_LVDS`, `VC5_CMOS2`, `VC5_CMOSD`, and `VC5_HCSL25`, numbered 0 through 6. There is no include guard in the visible content and no functions or structs.

## Control Flow and State
No control flow or state. Runtime behavior occurs in the VersaClock driver when it interprets output configuration properties.

## Dependencies and Integration Points
Used by DTS nodes for VersaClock-compatible clock generators to select output signaling mode. The matching driver must map these values to register programming.

## Risks and Test Signals
The main risk is mismatched output electrical mode, which can break board-level clock delivery. Test signals include DT schema validation and hardware tests that verify each configured output has the expected signal type and frequency.
