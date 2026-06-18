# sources/distributed-fs/ceph-client/sound/soc/sof/intel/lnl.c

Purpose: adapts Meteor Lake-style IPC4 HDA ops for Lunar Lake/ACE2 with extended multi-link offload, SoundWire IRQ differences, and LNL chip descriptor data.

Important APIs: `sof_lnl_set_ops()` starts from `sof_mtl_set_ops()`, then overrides probe/remove/resume/runtime_resume to enable DMIC/SSP offload and overrides `post_fw_run`. `lnl_dsp_check_sdw_irq()`, `lnl_dsp_disable_interrupts()`, and `lnl_sdw_check_wakeen_irq()` provide descriptor callbacks. `lnl_chip_info` defines five cores, ACE2 IP version, LNL ROM status register, extended SoundWire link-count checks, MTL boot/power helpers, and LNL-specific IRQ hooks.

Control flow: probe/resume first runs common HDA behavior and then enables offload on SSP and DMIC alternate links with `hdac_bus_eml_enable_offload()`. remove disables offload before common remove. post_fw_run marks IMR boot support and creates `skip_imr_boot` debugfs without starting SoundWire again.

State and persistence: modifies multi-link offload register state, `imrboot_supported`, debugfs bool, and static ops passed by caller. No separate persistent LNL state is introduced.

Dependencies and integration: depends on `mtl.c`, `hda-mlink.c`, SoundWire global WAKESTS behavior, and HDA common probe/PM.

Risks and test signals: risks include offload enable/disable errors during PM, dspless path skipping overrides, wake IRQ detection range, and inherited MTL behavior mismatches. Test LNL probe/remove/runtime resume, offload bits for DMIC/SSP, SoundWire IRQ/wake, IMR boot debugfs, and dspless mode.
