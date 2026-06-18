# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/audioreach.h

## Purpose
`audioreach.h` defines the AudioReach/APM ABI constants, packed command payload structures, topology graph structs, module configuration structs, and function prototypes used by `audioreach.c` and other QDSP6 APM code. It is the contract layer between Linux ASoC topology/DAI code and Qualcomm DSP graph commands.

## Important APIs, types, and constants
The header lists AudioReach module IDs for shared memory, gain, PCM enc/dec/cnv, I2S, SAL, MFC, logging, codec DMA, MP3/AAC/FLAC/OPUS, DisplayPort, and speaker protection. It defines APM graph commands, shared-memory map/unmap commands, data buffer commands, EOS commands, media-format IDs, data formats, channel/PCM constants, and many `PARAM_ID_*` values.

Packed structs cover shared memory map/unmap, buffer done responses, PCM/compressed media formats, APM command headers, module parameter blocks, subgraph/container/module graph config, I2S/DP/HW endpoint configs, logging, speaker protection, SAL, MFC, codec DMA, clock config, volume, and placeholder real-module IDs. Runtime topology structs include `audioreach_graph_info`, `audioreach_sub_graph`, `audioreach_container`, `audioreach_module`, and `audioreach_module_config`.

Public functions include packet allocators, `audioreach_alloc_graph_pkt()`, `audioreach_tplg_init()`, command send helpers, `audioreach_set_media_format()`, EOS, gain/volume, u32 param setting, compressed parameter setup, and graph buffer freeing.

## Control flow and integration
The header itself has no flow. Its types are consumed by topology parsing, graph open construction, APM DAI configuration, and GPR command submission. The list-based graph structs establish the traversal model used in `audioreach_alloc_graph_pkt()`: graph info owns subgraphs, subgraphs own containers, and containers own modules.

## State and persistence behavior
The ABI structs are packed to match DSP wire format and should not gain implicit padding. Runtime graph structs use kernel lists and pointers to connect parsed topology state to ALSA widgets and module private data. No persistent storage exists, but structure layout is effectively persistent as a DSP ABI.

## Dependencies and integration points
The header depends on Linux types, APR/GPR types, ALSA SoC and codec UAPI types, and `snd_ar_tokens.h`. It is integrated with `q6apm`, topology parsing, APM DAI paths, and DSP firmware command handling.

## Risks and test signals
Risks include duplicate or inconsistent defines, ABI packing mistakes, flexible-array size errors, and parameter ID drift against DSP firmware. Test signals include successful topology parsing, graph open on real firmware, media-format programming for every supported module ID, compressed codec playback, and build checks for packed structure layout warnings.
