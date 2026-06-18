<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo_dev.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo_dev.h

## Purpose
This header defines the device descriptor and operation table for external DVO transmitter chip drivers.

## Important APIs, Types, and Functions
`struct intel_dvo_device` records chip name, type, DVO port, GPIO/I2C bus selection, target address, ops pointer, chip private data, and I2C adapter. `struct intel_dvo_dev_ops` provides chip hooks for `init`, `dpms`, `mode_valid`, `mode_set`, `detect`, `get_hw_state`, `destroy`, and optional `dump_regs`. Extern declarations expose ops for sil164, ch7xxx, ivch, tfp410, ch7017, and ns2501.

## Control Flow
There is no implementation flow. `intel_dvo.c` uses the ops table to probe chips, validate modes, program modes, detect connectors, and clean up private state.

## State and Persistence Behavior
The descriptor is copied into `struct intel_dvo`; `dev_priv` and `i2c_bus` are mutable chip-driver state. The ops contract assumes `mode_set()` runs while output is disabled and `dpms()` handles the final on/off transition.

## Dependencies and Integration Points
It depends on register definitions for `enum port`, display limits, DRM mode status, display modes, and Linux I2C adapters. It is the ABI between generic DVO glue and chip-specific transmitter modules.

## Risks
Incorrect ops implementation can leave external transmitters powered or misprogrammed. `init()` comments mention returning NULL although the signature is `bool`, so implementers must follow actual return semantics. Chip hooks should only reject output-specific mode constraints in `mode_valid()`, leaving CRTC limits to generic code.

## Test Signals
Signals include successful probe/destroy for each chip driver, mode validation against chip limits, I2C transaction traces, DPMS on/off behavior, register dumps for debug builds, and hardware state readout matching generic DVO register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo_dev.h -->
