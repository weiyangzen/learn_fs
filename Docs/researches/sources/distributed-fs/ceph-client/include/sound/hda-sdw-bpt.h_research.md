# sources/distributed-fs/ceph-client/include/sound/hda-sdw-bpt.h

## Purpose
This header declares the HDA/SoundWire Bulk Payload Transport helper API and disabled-feature stubs.

## Important APIs, Types, and Functions
Enabled builds expose `hda_sdw_bpt_open()`, `hda_sdw_bpt_send_async()`, `hda_sdw_bpt_wait()`, `hda_sdw_bpt_close()`, and `hda_sdw_bpt_get_buf_size_alignment()`. The open/close APIs manage TX/RX `hdac_ext_stream` objects and DMA BDL buffers with byte counts and bandwidth values. Disabled builds warn once and return `-EOPNOTSUPP`, with alignment returning zero.

## Control Flow
Callers open a BPT session for a SoundWire link, launch asynchronous TX/RX transfer, wait for completion, then close and release streams/buffers. Alignment helper lets callers size DMA buffers according to bandwidth requirements.

## State and Persistence
BPT session state is represented by returned HDA extended stream pointers and DMA buffers. It is transient and should not persist beyond open/send/wait/close.

## Dependencies and Integration Points
It depends on `linux/device.h`, forward-declared HDA stream and ALSA DMA buffer types, SOF HDA SoundWire support, and DMA buffer management.

## Risks and Edge Cases
Callers must handle `-EOPNOTSUPP` stubs and avoid using uninitialized stream pointers after failed open. TX/RX bandwidth and buffer sizes must match hardware alignment. Async send requires disciplined wait/close ordering.

## Test Signals
Enabled/disabled build coverage, failed-open cleanup, buffer alignment checks, async completion timeout/error paths, and repeated open/send/wait/close cycles validate the API.
