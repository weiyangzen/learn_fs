# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/audioreach.c

## Purpose
`audioreach.c` implements helper routines for Qualcomm AudioReach/APM graph and module control over GPR. It allocates packets, builds graph-open payloads from topology data, sends synchronous commands, programs module media formats, configures shared-memory endpoints, sets gain/volume and module enable parameters, and sends EOS for shared-memory playback.

## Important APIs, types, and functions
Packet allocation helpers include `audioreach_alloc_pkt()`, `audioreach_alloc_apm_pkt()`, `audioreach_alloc_cmd_pkt()`, and `audioreach_alloc_apm_cmd_pkt()`, all backed by `__audioreach_alloc_pkt()`. `audioreach_alloc_graph_pkt()` constructs an `APM_CMD_GRAPH_OPEN` payload containing subgraph config, container config, module list, module properties, and module connections.

Synchronous command APIs are `audioreach_send_cmd_sync()` and `audioreach_graph_send_cmd_sync()`. Module/media-format APIs include `audioreach_set_media_format()`, `audioreach_compr_set_param()`, `audioreach_send_u32_param()`, `audioreach_gain_set_vol_ctrl()`, `audioreach_shared_memory_send_eos()`, and `audioreach_graph_free_buf()`. Static helpers handle I2S, DisplayPort, codec DMA, shared memory, PCM/MFC, compressed formats, data logging, SAL, gapless, gain, and speaker-protection modules.

## Control flow
Graph-open construction first counts subgraphs, containers, modules, and connections, computes aligned payload sizes, allocates an APM command packet, lays out each parameter block in sequence, and calls `audioreach_populate_graph()` to fill module/connection objects from topology lists. Command sending serializes through a mutex, clears the result state, sends via either a GPR device or GPR port, waits up to five seconds for the expected opcode or response opcode, and maps timeout/DSP errors to Linux errors.

`audioreach_set_media_format()` dispatches on `module->module_id`. Hardware endpoints receive HW media format plus interface/frame-size/power config. PCM-like modules receive PCM output format configs. Shared-memory endpoints receive `PARAM_ID_MEDIA_FORMAT` or compressed media format packets. Some modules require sequencing, such as enabling data logging after config, enabling SAL limiter after output config, or enabling speaker-protection modules after mode configuration.

## State and persistence behavior
Most state is transient packet memory allocated with `kzalloc()` and freed through `__free(kfree)` cleanup or explicit `kfree()`. Command completion state is stored in `graph->result`, `graph->lock`, and `graph->cmd_wait`, or in caller-provided result/lock/wait structures. `audioreach_graph_free_buf()` persists stream buffer state changes by clearing `rx_data` and `tx_data` buffer pointers and period counts under the graph lock. No disk state is written.

## Dependencies and integration points
The file depends on GPR/APR packet definitions, `q6apm` graph and port APIs, AudioReach ABI constants/types from `audioreach.h`, ALSA codec and PCM params, and topology-provided `audioreach_graph_info` lists. It is built into `snd-q6apm` and is used by APM DAI/topology paths to translate ALSA/topology parameters into DSP commands.

## Risks and test signals
Risks include payload size miscalculation for variable-length channel maps, incomplete channel mapping for more than four channels in helper defaults, timeout handling if callbacks race or return a different opcode, and inconsistent ownership because most packet paths use cleanup attributes but speaker-protection VI manually frees. Compressed format setup uses a base payload size that may not include codec-specific payload lengths, so codec validation is important. Tests should include graph open for multi-container topologies, media-format setup for PCM/I2S/DP/codec-DMA/shared-memory/compressed paths, timeout/error injection, EOS delivery, and KASAN/KMSAN coverage for variable-size payloads.
