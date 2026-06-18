# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-mfld-platform-compress.c

## Purpose
This file implements ALSA compressed-audio operations for the Atom SST ASoC platform. It adapts `snd_compr_stream` lifecycle, codec parameters, fragment callbacks, drain callbacks, timestamps, acknowledgements, and metadata operations to the low-level `compress_sst_ops` exported by the SST DSP driver.

## Important APIs, types, and functions
The exported object is `sst_platform_compress_ops`. Stream setup uses `sst_platform_compr_open()`, `sst_platform_compr_free()`, and `sst_platform_compr_set_params()`. Runtime control is handled by `sst_platform_compr_trigger()`, `sst_platform_compr_pointer()`, `sst_platform_compr_ack()`, `sst_platform_compr_set_metadata()`, `sst_platform_compr_get_caps()`, and `sst_platform_compr_get_codec_caps()`. Firmware callbacks are bridged through `sst_compr_fragment_elapsed()` and `sst_drain_notify()`.

## Control flow
Open allocates `struct sst_runtime_stream`, obtains the registered global `sst` DSP device, stores `sst->compr_ops`, powers on the LPE, and attaches runtime private data. `set_params` fills generic stream mapping via `sst_fill_stream_params()`, translates ALSA codec IDs for MP3 and AAC into SST codec parameters, sets ring buffer address/size and fragment size, installs fragment/drain callbacks, and calls `compr_ops->open()` to allocate a firmware stream ID. Trigger commands dispatch start, stop/drop, full drain, partial drain, pause, and pause release to the low-level driver. Pointer reads firmware timestamps and calculates the ring-buffer byte offset from `copied_total`.

## State and persistence behavior
Per-stream state is a heap-allocated `sst_runtime_stream` stored in `runtime->private_data`. It holds the firmware stream ID, cumulative `bytes_written`, and low-level ops pointer. No on-disk persistence exists. Power is reference-managed through the low-level driver on open/free.

## Dependencies and integration points
The file depends on ALSA compressed offload APIs, ASoC component compressed callbacks, the global `sst` registration from `sst-mfld-platform-pcm.c`, and the low-level compressed ops from `sst_drv_interface.c`. It uses `virt_to_phys()` on the compressed runtime buffer to provide firmware ring-buffer addresses.

## Risks and edge cases
Only MP3 and AAC are supported, and AAC accepts only ADTS and RAW stream formats. `sst_platform_compr_free()` powers down before closing the firmware stream, which depends on low-level power handling tolerating that order. Pointer offset calculation mutates a local copy of `copied_total` with `do_div()`. The code assumes a single contiguous compressed buffer and one scatter-gather entry.

## Test signals
Test MP3 and AAC open/set_params/start/stop, ADTS and RAW AAC formats, invalid codec rejection, fragment elapsed callbacks, drain and partial-drain notifications, metadata calls, timestamp progression, ack byte accounting, caps reporting, and cleanup after stream allocation failure.
