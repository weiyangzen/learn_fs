# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-mfld-dsp.h

## Purpose
This header defines the Merrifield/Baytrail SST firmware IPC ABI: mailbox offsets, IPC message IDs, firmware and stream parameter layouts, timestamp structures, byte-stream control format, codec parameter unions, allocation payloads, and helper constants used by the ASoC platform and low-level SST driver.

## Important APIs, types, and functions
Important constants include mailbox/timestamp offsets (`SST_MAILBOX_SIZE`, `SST_MAILBOX_SEND`, `SST_TIME_STAMP_MRFLD`), IPC command IDs (`IPC_IA_ALLOC_STREAM_MRFLD`, `IPC_IA_START_STREAM_MRFLD`, `IPC_IA_DRAIN_STREAM_MRFLD`, `IPC_IA_SET_PARAMS`), asynchronous firmware IDs (`IPC_IA_FW_INIT_CMPLT_MRFLD`, `IPC_SST_PERIOD_ELAPSED_MRFLD`, `IPC_IA_BUF_UNDER_RUN_MRFLD`), and `SST_ASYNC_DRV_ID`.

The IPC headers are `struct ipc_dsp_hdr`, `union ipc_header_high`, `union ipc_header_mrfld`, and legacy `union ipc_header`. Firmware metadata and response layouts include `struct ipc_header_fw_init`, `struct snd_sst_fw_version`, and `struct sst_fw_build_info`. Stream configuration is expressed through `struct snd_sst_params`, `struct snd_sst_alloc_mrfld`, `struct snd_sst_alloc_params_ext`, `struct snd_sst_stream_params`, `union snd_sst_codec_params`, and codec-specific PCM/MP3/AAC/WMA structs. Runtime data exchange uses `struct snd_sst_tstamp`, `struct snd_sst_async_msg`, `struct snd_sst_runtime_params`, and `struct snd_sst_bytes_v2`.

## Control flow
The header does not execute code. At runtime, platform code fills `snd_sst_params`, low-level stream code converts it to `snd_sst_alloc_mrfld`, IPC helpers wrap payloads with `ipc_dsp_hdr` and `ipc_header_mrfld`, and interrupt handling decodes asynchronous message IDs and timestamp buffers according to these layouts.

## State and persistence behavior
The structures model transient mailbox and firmware state. Timestamp structures persist in shared mailbox memory per stream while a stream exists. `snd_sst_bytes_v2` carries cached ASoC controls from the platform side into one IPC transaction.

## Dependencies and integration points
This file is included by `sst-mfld-platform.h` and low-level SST implementation files. It is the binary ABI with SST firmware, so it integrates ALSA PCM/compress semantics with firmware allocation, drain, pause, resume, timestamp, byte-stream, and debug messages.

## Risks and edge cases
All mailbox payloads must remain 32-bit aligned as the header warns. Several structs are packed and include bitfields, so compiler/layout changes are high risk. Some codec fields are only partially populated by current callers. Mailbox sizes and scatter buffer counts are fixed; callers must not exceed `SST_MAILBOX_SIZE` or `MAX_NUM_SCATTER_BUFFERS`.

## Test signals
Validation includes firmware boot response decoding, PCM allocation, compressed MP3/AAC allocation, timestamp reads, byte-stream set/get controls, period elapsed and drain callbacks, async error logging, and negative tests for unsupported codecs, invalid stream IDs, and oversized byte-stream payloads.
