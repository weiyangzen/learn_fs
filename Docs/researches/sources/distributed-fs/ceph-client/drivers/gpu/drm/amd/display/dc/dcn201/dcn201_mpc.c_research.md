# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_mpc.c

## Purpose
Implements the DCN201 multiple-pipe combiner object by reusing DCN1/DCN2 MPC helpers and adding output rate/flow-control programming.

## Important APIs, Types, And Functions
`mpc201_set_out_rate_control()` programs `MPC_OUT_RATE_CONTROL_DISABLE`, `MPC_OUT_RATE_CONTROL`, and optional flow-control mode/counts on the output mux register indexed by OPP. `mpc201_init_mpcc()` initializes each software MPCC node to defaults. `dcn201_mpc_funcs` delegates plane insertion/removal, blending, denorm, output CSC/gamma, memory power, background color, and MPCC state operations to MPC1/MPC2 helpers, with DCN201 rate control. `dcn201_mpc_construct()` initializes the object and MPCC array.

## Control Flow
Construction sets context, function table, register descriptors, zeroes in-use mask, stores `num_mpcc`, and initializes all `MAX_MPCC` MPCC nodes. Rate-control calls update mux fields and conditionally writes flow-control fields only when a `flow_control` pointer is provided.

## State And Persistence
Software state includes `mpcc_in_use_mask`, `num_mpcc`, the MPCC array inside the base object, and register descriptor pointers. Hardware state persists in MPC output mux registers and inherited MPC registers.

## Dependencies And Integration Points
Depends on `dcn201_mpc.h`, `reg_helper`, and inherited DCN20 MPC helper functions. Integrated into the resource pool as the compositor for DCN201 display pipes.

## Risks
`opp_id` is used directly as `MUX[opp_id]`; callers must pass a valid output index. All `MAX_MPCC` entries are initialized even if `num_mpcc` is smaller, so later allocation code must respect `num_mpcc`. Flow-control values are unvalidated here.

## Test Signals
Plane composition, MPCC allocation/free, output CSC/gamma, rate-control toggling, DWB flow control, and register readback of mux fields are useful signals.
