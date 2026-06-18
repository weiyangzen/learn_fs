<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/messages.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/messages.h

## Purpose
Firmware IPC ABI definition for CATPT. It declares message headers, status values, stream/pin/path/module identifiers, audio formats, ring/memory descriptors, stream and mixer reply structures, SSP format descriptors, Dx context descriptors, notification payloads, and IPC wrapper prototypes.

## APIs, Types, and Functions
Key types include `union catpt_global_msg`, `union catpt_stream_msg`, `union catpt_notify_msg`, `struct catpt_fw_version`, `struct catpt_audio_format`, `struct catpt_ring_info`, `struct catpt_module_entry`, `struct catpt_stream_info`, `struct catpt_ssp_device_format`, `struct catpt_dx_context`, `struct catpt_mixer_stream_info`, `struct catpt_fw_ready`, `struct catpt_notify_position`, and `struct catpt_notify_glitch`. Macros `CATPT_MSG()`, `CATPT_GLOBAL_MSG()`, `CATPT_STREAM_MSG()`, and `CATPT_STAGE_MSG()` initialize packed headers.

## Control Flow, State, and Persistence
The header carries no executable state but defines the binary layout persisted across host/DSP mailboxes, firmware boot config, Dx save/restore records, stream IDs, and firmware register addresses. Packed structs ensure mailbox payloads match DSP expectations; enums determine how PCM stream templates map to firmware modules and pin IDs.

## Dependencies and Integration
Included by all CATPT files through `core.h` or directly. Its definitions integrate firmware command wrappers, IPC response parsing, PCM stream creation, sysfs firmware-version reads, and coredump firmware-info extraction.

## Risks and Test Signals
Risks include compiler-dependent packed bitfield ordering, ABI drift from firmware, accidental enum renumbering, `CATPT_CHANNELS_MAX` and `SAVE_MEMINFO_MAX` mismatches, and bool packing in payload structs outside this header. Test signals are stable compile-time structure sizes on supported architectures, firmware accepting all command headers, correct stream IDs/register addresses in replies, valid firmware-ready mailbox offsets, and notification parsing for position/glitch events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/messages.h -->
