# sources/distributed-fs/ceph-client/arch/x86/include/asm/platform_sst_audio.h

Purpose: defines Intel SST/Merrifield audio platform data structures and firmware pipeline identifiers used by platform audio drivers.

Important APIs, types, and functions: constants include `MAX_NUM_STREAMS_MRFLD` and `MAX_NUM_STREAMS`. Enums define `sst_audio_task_id_mrfld` and `sst_audio_device_id_mrfld` pipeline IDs for output and input paths. Data structures include `sst_dev_stream_map`, `sst_platform_data`, `sst_info`, `sst_lib_dnld_info`, `sst_res_info`, `sst_ipc_info`, and `sst_platform_info`. It declares `add_sst_platform_device()`.

Control flow: no implementation is present. Platform code passes these tables to SST audio drivers so they can map ALSA/device streams to firmware task IDs, resource windows, IPC mailboxes, DSP memory regions, and library download metadata.

State and persistence: structures describe static or firmware/platform runtime state. No state is allocated here.

Dependencies and integration points: consumed by Intel SST platform, ACPI/platform-device setup, DSP firmware loader, IPC, DMA, and ALSA SoC components.

Risks: pipeline IDs are firmware ABI. Wrong resource offsets, mailbox locations, DMA limits, or suspend behavior flags can break DSP boot, audio routing, or resume. Stream maps must match platform-specific firmware topology.

Test signals: Merrifield/SST device probe, firmware load, playback/capture on each mapped pipeline, suspend/resume with `streams_lost_on_suspend`, IPC mailbox traffic, resource mapping from ACPI indices, and module/library download paths.
