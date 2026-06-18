# sources/distributed-fs/ceph-client/drivers/slimbus/stream.c

## Purpose
This file implements the exported SLIMbus stream lifecycle used by audio clients: allocate, prepare, enable, disable, unprepare, and free. It maps audio stream configuration to SLIMbus port association and channel definition messages.

## Important APIs, Types, And Functions
Exports are `slim_stream_allocate()`, `slim_stream_prepare()`, `slim_stream_enable()`, `slim_stream_disable()`, `slim_stream_unprepare()`, and `slim_stream_free()`. Internal helpers include `slim_connect_port_channel()`, `slim_disconnect_port()`, `slim_define_channel()`, `slim_define_channel_content()`, `slim_activate_channel()`, `slim_deactivate_remove_channel()`, `slim_get_prate_code()`, and `slim_get_segdist_code()`.

## Control Flow
Allocation creates a runtime, names it, and links it to the SLIMbus device stream list. Prepare validates that ports are not already allocated, allocates per-port state, records rate/bps/direction, chooses PUSH/PULL/ISO protocol from sample rate relative to superframe rate, computes rate multiplier, initializes channel fields, and sends connect-source or connect-sink messages for each selected port. Enable either delegates to a controller-specific `enable_stream` callback or sends a reconfiguration sequence, defines each channel and content, activates channels, marks ports configured, and reconfigures now. Disable optionally calls controller `disable_stream`, then deactivates/removes channels inside a reconfiguration. Unprepare disconnects ports and frees port state. Free removes the stream from the device list.

## State, Persistence, And Dependencies
State is the runtime allocation, list membership, per-port state, channel state, protocol, rate, bps, and rate multiplier. It depends on SLIMbus core transfer, public stream config structures, and ALSA PCM direction constants.

## Integration Points
ASoC DPCM operations map naturally to these calls: startup, hw_params, trigger start, trigger pause/stop, and shutdown. Controller drivers may override stream enable/disable for hardware-specific aggregate commands.

## Risks
Several helper calls ignore return values in loops, so prepare and enable can report success after failed port or channel transfers. State fields are often advanced before transfer success. If `slim_get_prate_code()` fails after port allocation, `rt->ports` is leaked unless the caller unprepares. Segment distribution only accepts table values and returns `-EINVAL`, but callers do not check all helper errors.

## Test Signals
Exercise supported and unsupported sample rates, multiple-port masks, playback and capture direction mapping, controller-specific enable path, generic reconfiguration path, transfer-failure injection, repeated prepare rejection, and clean list removal on free.
