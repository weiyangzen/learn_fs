# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn401/dcn401_init.h

## Purpose
`dcn401_init.h` is a small public declaration header for DCN401 hardware sequencer initialization. It forwards `struct dc` and declares `dcn401_hw_sequencer_init_functions()`.

## Important API
- `void dcn401_hw_sequencer_init_functions(struct dc *dc);` installs DCN401 public and private hardware sequencer function tables.

## Control Flow, State, and Integration
The header has no persistent state and no implementation logic. Its only role is to let the DCN401 resource construction path call the vtable initializer without importing implementation internals.

## Risks and Test Signals
Risk is limited to declaration/definition mismatch or include-guard mistakes. Compile coverage is the primary signal; runtime confidence comes indirectly from successful DCN401 device initialization using the installed vtables.
