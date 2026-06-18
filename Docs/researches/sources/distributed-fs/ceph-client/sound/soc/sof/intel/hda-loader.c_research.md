# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-loader.c

Purpose: `hda-loader.c` is the generic HDA code-loader implementation for newer HDA SOF platforms. It prepares HDAC extended streams for firmware or IPC4 library loading, initializes DSP ROM boot, supports IMR restore, manages persistent code-loader DMA buffers, handles ICCMAX boot, and parses Intel cAVS extended manifest data.

Important APIs: exported functions include `hda_cl_prepare()`, `cl_dsp_init()`, `hda_cl_trigger()`, `hda_cl_cleanup()`, `hda_cl_copy_fw()`, `hda_dsp_cl_boot_firmware_iccmax()`, `hda_dsp_cl_boot_firmware()`, `hda_dsp_ipc4_load_library()`, and `hda_dsp_ext_man_get_cavs_config_data()`. The module parameter `persistent_cl_buffer` controls whether code-loader DMA memory is retained across boots and library loads.

Control flow: cold boot prepares a playback code-loader stream with the stripped firmware payload, optionally copies payload into a persistent DMA buffer, retries ROM initialization up to `HDA_FW_BOOT_ATTEMPTS`, processes SoundWire wake events after ROM init on resume, triggers DMA, waits for `FW_ENTERED`, cleans up the stream, and returns the init core mask. IMR restore skips DMA when supported and valid, falling back to cold boot on failure. `cl_dsp_init()` powers up host-managed cores, sets SSP clock consumer/provider mode, sends ROM_CONTROL with stream tag, runs the init core, waits for IPC DONE, powers down non-boot cores, enables IPC interrupts, and waits for the requested ROM status.

State and persistence behavior: state includes `hda->cl_dmab`, `hda->iccmax_dmab`, `cl_dmab_contains_basefw`, `boot_iteration`, `booted_from_imr`, `skip_imr_boot`, enabled core mask, per-core refcounts, SoundWire wake state, and parsed `clk_config_lpro`. Library loading may resize the persistent DMA buffer and marks it as no longer containing base firmware.

Dependencies and integration: it depends on HDAC stream helpers, HDA DSP core/power functions, IPC4 firmware library messages, extended manifest structures, SoundWire wake processing, and SOF firmware payload validation.

Risks and test signals: risks include IMR boot after memory loss, stale persistent DMA content, library reload skipping when restore state is wrong, cleanup errors masking primary boot failures, ROM_CONTROL stream-tag errors, and manifest size parsing. Test cold boot, IMR boot fallback, IPC4 two-stage and single-step library loading, persistent buffer resize, ICCMAX boot cleanup/guardband restore, SoundWire wake processing after resume, and LPRO manifest parsing.
