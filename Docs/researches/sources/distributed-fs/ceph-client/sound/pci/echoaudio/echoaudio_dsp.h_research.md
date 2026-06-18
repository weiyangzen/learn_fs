# sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio_dsp.h

## Purpose

`echoaudio_dsp.h` defines the DSP ABI shared by all Echoaudio PCI card personalities. It contains family selection, DSP register offsets, vector command values, clock and digital-mode bit definitions, audio-format encodings, timeout constants, SG entry layout, and the packed DSP communication page layout.

## Important APIs, Types, and Functions

Important definitions include family gates `ECHOGALS_FAMILY`, `ECHO24_FAMILY`, `ECHO3G_FAMILY`, and `INDIGO_FAMILY`; register offsets `CHI32_CONTROL_REG`, `CHI32_STATUS_REG`, `CHI32_VECTOR_REG`, and `CHI32_DATA_REG`; status bits such as `CHI32_STATUS_HOST_READ_FULL`, `CHI32_STATUS_HOST_WRITE_EMPTY`, `CHI32_STATUS_IRQ`, and host flags HF3/HF4/HF5; vector commands such as `DSP_VC_RESET`, `DSP_VC_START_TRANSFER`, `DSP_VC_STOP_TRANSFER`, `DSP_VC_WRITE_CONTROL_REG`, `DSP_VC_UPDATE_FLAGS`, and `DSP_VC_SET_VMIXER_GAIN`; and clock constants for GLDM, GML, E3G, Mia, Layla24, and Indigo Express hardware. `struct sg_entry` and `struct comm_page` are the central DMA-visible types.

## Control Flow

The header is consumed through compile-time inclusion. Each card wrapper defines a family and feature macros before including common source files; this header then selects DSP type, read timeout, command values, and hardware constants. Runtime code fills `struct comm_page`, sends vector commands, and expects the DSP firmware to read fixed offsets documented in the struct comments.

## State and Persistence Behavior

`struct comm_page` is persistent shared state between host and DSP. It stores flags, sample rate, handshake, start/stop/reset masks, per-pipe audio formats, SG-list physical addresses, DMA positions, meters, line levels, monitor matrix, MIDI buffers, clock/status fields, control registers, and vmixer levels. The layout is an ABI and must not drift; `echoaudio_dsp.c` checks the MIDI output offset at runtime.

## Dependencies and Integration Points

The header is included indirectly by card modules through `echoaudio.h` and is tightly coupled to firmware binaries under `ea/*.fw`. It also aligns with ALSA capabilities exposed by each card wrapper, because PCM formats and rates must map to supported DSP audio-format and clock constants.

## Risks and Test Signals

Changing constants or struct layout can break firmware communication even when the kernel still builds. Test signals include `offsetof(struct comm_page, midi_output) == 0xbe0`, successful DSP command handshakes, correct clock detection bits reported in ALSA controls, working SG DMA, and build coverage for Echogals, Echo24, 3G, and Indigo families.
