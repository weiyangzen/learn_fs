# sources/distributed-fs/ceph-client/include/dt-bindings/clock/sophgo,sg2042-rpgate.h

## Purpose
`sophgo,sg2042-rpgate.h` defines gate IDs for SG2042 reset/power or receive/processing gate-style clock control.

## Important APIs, types, and functions
The exported API is a contiguous set of `GATE_CLK_*` macros. It starts with `GATE_CLK_RXU0` through `GATE_CLK_RXU23`, continues with `GATE_CLK_RXU24`, `GATE_CLK_RXU25`, and then `GATE_CLK_MP0` through `GATE_CLK_MP15`. There are no functions or structs.

## Control flow
DTS consumers or provider data reference these gate IDs. Runtime enable/disable behavior is implemented by the SG2042 rpgate clock driver, which maps each ID to a hardware gate bit.

## State and persistence
The header has no state. Gate enable state lives in SG2042 hardware registers and is ABI-addressed by these numeric constants.

## Dependencies and integration points
It integrates with SG2042 DTS, the rpgate clock provider, multi-processor or receive-unit clock domains, and any consumers that require per-unit gate control.

## Risks and test signals
Risks include off-by-one gate-to-bit mapping, assuming RXU and MP gates are independent providers when they share one ID space, and changing the contiguous ABI. Test signals include provider registration, per-gate enable/disable tests, debugfs gate state inspection, and functional tests for devices or cores behind RXU/MP gates.
