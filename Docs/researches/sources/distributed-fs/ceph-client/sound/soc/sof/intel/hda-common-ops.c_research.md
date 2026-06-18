# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-common-ops.c

Purpose: `hda-common-ops.c` defines `sof_hda_common_ops`, the shared `struct snd_sof_dsp_ops` baseline for Skylake and newer HDAudio-based SOF platforms. Generation-specific files clone this table and override only the operations that differ.

Important fields: the table wires early/proper/late probe and remove to `hda_dsp_*`, block and mailbox I/O to generic SOF helpers, mailbox/window offsets to HDA IPC helpers, machine selection to HDA machine helpers, debug dumping to `hda_dsp_dump`, PCM operations to HDA DSP stream callbacks, firmware loading to raw firmware loading, pre-run and run to the HDA code-loader path, manifest parsing to `hda_dsp_ext_man_get_cavs_config_data`, trace callbacks, IPC client registration, DAI drivers to `skl_dai`, chain-DMA detection, PM callbacks, hardware info flags, and Xtensa architecture ops.

Control flow and integration: platform ops init functions in `apl.c`, `cnl.c`, and later family files copy this structure, install protocol-specific IPC send/IRQ/dump/power callbacks, and set platform debug maps or chip-specific boot functions. The common table makes HDA platforms behave consistently for probe, PCM, PM, firmware loading, and machine registration.

State and persistence behavior: the object itself is constant and exported, but consumers copy it into mutable per-family global operation structures. That copy pattern means later mutation affects the platform global ops used by devices of that family.

Dependencies and risks: the table depends on many exports from HDA controller, DAI, DSP, IPC, loader, trace, machine, and PCM files. Risks are missing default callbacks, stale function pointers after API changes, and accidental sharing of mutable per-family ops. Test signals include booting at least one IPC3 and one IPC4 HDA platform, PCM playback/capture, runtime/system suspend, trace start/stop, DAI registration count, and no unresolved symbol or namespace warnings.
