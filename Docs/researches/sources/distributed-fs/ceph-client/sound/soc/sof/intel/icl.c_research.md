# sources/distributed-fs/ceph-client/sound/soc/sof/intel/icl.c

Purpose: provides Ice Lake-specific SOF HDA DSP ops and chip descriptor. It layers ICL power/firmware behavior over common HDA ops, with IPC3/IPC4 selection and HPRO core handling.

Important APIs: `sof_icl_ops_init()` copies `sof_hda_common_ops`, selects IPC3 CNL or IPC4 CNL handlers, allocates IPC4 private data when needed, sets debug maps, post-fw-run, ICCMAX code-loader boot, stall callback, core_get, and DAI ops. `icl_dsp_post_fw_run()` starts SoundWire on first boot, marks IMR boot support if firmware reports D3 persistent, enables SDW interrupts, powers/stalls core 3 for HPRO mode, and reenables clock/power gating. `icl_chip_info` describes cores, IPC registers, ROM status, SSP/SDW bases, callbacks, and platform string.

Control flow: ops_init runs during PCI descriptor setup; firmware boot later calls post_fw_run, which conditionally performs first-boot SoundWire/IMR setup and always restores clock gating. `icl_dsp_core_stall()` masks requested cores to host-managed cores before setting CSTALL.

State and persistence: updates global `sof_icl_ops`, `sdev->private` for IPC4, `enabled_cores_mask`, core refcount for core 3, and `hdev->imrboot_supported`.

Dependencies and integration: depends on HDA common ops, CNL IPC handlers, IPC4 firmware data, SoundWire startup, and code loader helpers.

Risks and test signals: risks include static ops mutation across devices, IPC type branch coverage, core 3 HPRO power/refcount imbalance, and IMR support detection. Test ICL/JSL probe with IPC3 and IPC4, first/subsequent boot, LPRO/HPRO configs, SoundWire startup failure, and core stall validation.
