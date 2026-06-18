# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-fw-reg.h

## Purpose
Defines the host-visible IPC4 firmware register memory layout used by the SOF driver for firmware status, ROM information, pipeline stream offsets, peak-volume telemetry, and link-position readings.

## APIs, Types, and Functions
This header has no functions. It defines `SOF_IPC4_INVALID_STREAM_POSITION`, register capacity constants, ABI version `SOF_IPC4_FW_REGS_ABI_VER`, ROM-info bit masks, and packed/aligned structures: `sof_ipc4_pipeline_registers`, `sof_ipc4_peak_volume_regs`, `sof_ipc4_llp_reading`, `sof_ipc4_llp_reading_extended`, `sof_ipc4_llp_reading_slot`, and top-level `sof_ipc4_fw_registers`.

## Control Flow, State, and Persistence
The structures describe shared memory populated by firmware and read by the kernel. `ipc4-pcm.c` reads `abi_ver` during PCM setup to decide whether delay reporting is supported, reads `pipeline_regs` for stream start/end offsets, and scans LLP slots to map a DAI gateway node id to its position counter. The invalid stream-position sentinel represents uninitialized stream statistics after reset or before first data movement.

## Dependencies and Integration
The layout relies on fixed IPC4 firmware ABI packing and 4-byte alignment. It integrates with SOF mailbox accessors, host/DAI copier node ids from topology, and PCM pointer/delay logic. The ROM status masks are available to platform code that reads `fw_status`, `lec`, `lnec`, or `rom_info`.

## Risks and Test Signals
The main risk is ABI drift between firmware and this host layout; a wrong offset corrupts delay math or status decoding. Capacity constants also cap the number of supported pipeline, peak-volume, GPDMA, SoundWire, EVAD, and core slots. Test signals are ABI version gating, correct mailbox offsets from `offsetof()`, valid stream offsets after playback, LLP slot node-id matching for HDA/GPDMA/SoundWire/EVAD paths, and graceful fallback when firmware reports an older ABI.
