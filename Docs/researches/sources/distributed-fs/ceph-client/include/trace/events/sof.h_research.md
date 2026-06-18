
# sources/distributed-fs/ceph-client/include/trace/events/sof.h

## Purpose
Defines Sound Open Firmware core tracepoints for widget setup/free, PCM pointer positions, IPC3 period elapsed reports, IPC stream position reception, and IPC4 firmware configuration.

## Important APIs, Types, and Functions
The `sof_widget_template` event class backs `sof_widget_setup` and `sof_widget_free`. Other events are `sof_ipc3_period_elapsed_position`, `sof_pcm_pointer_position`, `sof_stream_position_ipc_rx`, and `sof_ipc4_fw_config`. Fields include widget names, DSP component ids, host/Dai positions, wall-clock values, PCM delay, stream tag, and IPC4 firmware config values.

## Control Flow
SOF core and PCM code emit widget events during topology/widget lifecycle, position events while handling period elapsed or PCM pointer updates, stream-position traces when IPC replies arrive, and config traces when IPC4 firmware configuration is known.

## State and Persistence
The header owns no audio state. Trace records persist copied widget names and scalar position/config snapshots. Position values are time-sensitive diagnostics and must be interpreted relative to PCM stream activity.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h` and SOF audio structures at call sites. Integrates with ALSA SoC SOF topology, IPC3/IPC4 firmware communication, PCM runtime diagnostics, and audio latency debugging.

## Risks
Position traces can be high frequency. Widget names and component ids must match topology lifetimes. IPC version differences mean tools must distinguish IPC3 and IPC4 events. Misinterpreting host/Dai position units can lead to false latency conclusions.

## Test Signals
Signals include SOF topology load/unload, PCM playback/capture under tracing, period elapsed validation, IPC3 and IPC4 firmware boots, XRUN/latency tests, and trace output comparison to ALSA runtime position.
