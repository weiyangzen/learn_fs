<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof.h -->
# sources/distributed-fs/ceph-client/include/sound/sof.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/sof.h` is Top-level SOF kernel integration header
describing firmware state, DSP power states, IPC version selection, loadable file profiles, platform
data, and device descriptors used by SOF bus and platform drivers. The source was read as a complete
182-line header for this report.

## Important APIs, Types, and Functions

types: `snd_sof_dsp_ops`, `snd_sof_dev`, `sof_loadable_file_profile`, `snd_sof_pdata`,
`sof_dev_desc`; enums: `sof_fw_state`, `sof_dsp_power_states`, `sof_ipc_type`; functions/prototypes:
`sof_dai_get_mclk`, `sof_dai_get_bclk`, `sof_dai_get_tdm_slots`; macros/constants:
`__INCLUDE_SOUND_SOF_H`

## Control Flow

PCI/ACPI/platform discovery selects a `sof_dev_desc`, fills `snd_sof_pdata`, chooses
firmware/topology/library filenames, and then SOF core transitions through firmware loading, DSP
boot, IPC ready, machine-driver selection, and runtime DAI clock queries.

## State and Persistence Behavior

Persistent runtime state lives in `snd_sof_pdata`, the selected descriptor, firmware state enum
values, IPC type, machine driver pointer, platform device links, and per-device private data. The
header has no storage of its own.

## Dependencies and Integration Points

Direct includes: `linux/pci.h`, `sound/soc.h`, `sound/soc-acpi.h`. Integrates with ALSA core, ASoC
codec/card drivers, rawmidi/seq, firmware loading, or legacy card drivers depending on the matching
subsystem.

## Risks and Edge Cases

Risks include firmware/topology path mismatches, wrong IPC type for a DSP generation, descriptor
callbacks not matching the platform, stale machine descriptors, and DAI clock helper users assuming
topology private data is present.

## Test Signals

Test descriptor matching, firmware path fallback, IPC3 and IPC4 boot, topology loading, machine-
driver selection, D0/D3 transitions, and `sof_dai_get_mclk/bclk/tdm_slots` on DAIs with and without
clock data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof.h -->
