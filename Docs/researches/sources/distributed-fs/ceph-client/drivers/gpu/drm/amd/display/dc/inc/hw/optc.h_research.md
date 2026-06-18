# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/optc.h

## Purpose

`optc.h` defines the DCN Output Pipe Timing Combiner wrapper around the generic timing generator. OPTC combines ODM and OTG responsibilities: mapping OPP inputs into display output segments and generating timing signals.

## Important APIs, Types, And Functions

`struct optc` embeds `struct timing_generator base`, register/shift/mask tables, OPP count, timing limits, blank/sync limits, vstartup/vupdate/vready/pstate offsets, original patched timing, signal type, and max frame count. It declares `optc1_read_otg_state()` for reading OTG state into the shared timing-generator state struct.

## Control Flow

ASIC-specific constructors create an OPTC by filling the embedded timing-generator vtable and register tables. Higher layers call the base timing-generator functions, while implementation code uses the extra OPTC fields for limits, ODM segment count, DSC mode, and vupdate/pstate programming.

## State And Persistence Behavior

`optc` stores persistent software limits and the last patched timing information. Hardware state lives in OTG/ODM registers and can be read back through state-dump hooks.

## Dependencies And Integration Points

The file depends on `timing_generator.h`. It integrates with OPP output routing, ODM combine/split resource logic, DSC timing configuration, vblank/vupdate IRQ programming, and debug readout.

## Risks And Test Signals

Risks include invalid timing limits, stale original timing after patching, ODM segment mismatches, and incorrect vupdate/pstate offsets. Test signals include timing validation, ODM combine modes, DSC modes, vblank/vline IRQs, frame-count readback, and DCN register state dumps.
