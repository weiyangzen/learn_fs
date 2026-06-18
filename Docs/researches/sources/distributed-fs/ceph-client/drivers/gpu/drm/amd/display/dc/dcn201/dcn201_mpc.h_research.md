# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_mpc.h

## Purpose
Defines the DCN201 MPC register-field extensions, concrete MPC structure, and constructor prototype.

## Important APIs, Types, And Functions
Macros reuse DCN2.0 MPC register lists and add fields for `MPC_OUT_RATE_CONTROL`, disable, flow-control mode, and two flow-control counts. Types include `dcn201_mpc_registers`, `dcn201_mpc_shift`, `dcn201_mpc_mask`, and `dcn201_mpc`. `TO_DCN201_MPC()` converts the base object to the concrete object.

## Control Flow
No executable flow. Macro expansion controls which fields inherited MPC helpers and DCN201-specific rate control can access.

## State And Persistence
The concrete object extends `struct mpc` with MPCC usage tracking, MPCC count, and register descriptors. Hardware state is in MPC registers.

## Dependencies And Integration Points
Includes `dcn20/dcn20_mpc.h` and is used by `dcn201_mpc.c` and DCN201 resource construction.

## Risks
Field-list concatenation must include proper separators; a missing semicolon in macro expansion would break generated structs. Flow-control fields must match the hardware mux register layout.

## Test Signals
Compile-time structure generation plus runtime tests of rate control, flow control, MPCC state reading, and plane composition.
