# sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx_dsp_scb_types.h

## Purpose
`cs46xx_dsp_scb_types.h` is the host-side C description of the CS46xx DSP SPOS stream control block ABI. It does not run logic itself; it defines the exact 32-bit and paired 16-bit layouts that `dsp_spos.c`, `dsp_spos_scb_lib.c`, and `cs46xx_lib.c` write into BA1 parameter/sample memory for the on-chip signal processor. The comments are copied from Cirrus SP OS listing documentation, so this file is also the driver's primary executable specification for DMA requestors, task links, mixer inputs, sample-rate converters, SPDIF tasks, async foreground tasks, snoopers, and filters.

## Important APIs, types, and data layout
The file defines `___DSP_DUAL_16BIT_ALLOC(a,b)`, which reverses field order on big endian hosts so packed 16-bit pairs land in the DSP-visible order. Core reusable blocks are `struct dsp_basic_dma_req`, `struct dsp_scatter_gather_ext`, `struct dsp_volume_control`, and `struct dsp_generic_scb`. Task-specific SCBs include `dsp_spos_control_block`, `dsp_timing_master_scb`, `dsp_codec_output_scb`, `dsp_codec_input_scb`, `dsp_pcm_serial_input_scb`, `dsp_src_task_scb`, `dsp_decimate_by_pow2_scb`, `dsp_vari_decimate_scb`, `dsp_mix2_ostream_scb`, `dsp_mix_only_scb`, `dsp_async_codec_input_scb`, `dsp_spdifiscb`, `dsp_spdifoscb`, `dsp_asynch_fg_rx_scb`, `dsp_asynch_fg_tx_scb`, `dsp_output_snoop_scb`, `dsp_spio_write_scb`, `dsp_magic_snoop_task`, and `dsp_filter_scb`.

## Control flow and integration
Consumers instantiate these structs as static or stack values, cast them to `u32 *`, and write the first 16 dwords to parameter memory with `cs46xx_dsp_create_scb()`. Several structs intentionally duplicate the generic SCB header so offsets 9 and 10 still contain `next_scb`/`sub_list_ptr` and `entry_point`/`this_spb`; inline helpers in `dsp_spos.h` later patch those offsets directly.

## State and persistence behavior
The state represented here persists in DSP parameter memory, not in this header. With PM enabled, `cs46xx_dsp_create_scb()` duplicates the initial 16 dwords so `cs46xx_dsp_resume()` can restore SCBs after hardware reset, then reapply runtime link and volume updates tracked in `struct dsp_scb_descriptor`.

## Dependencies and integration points
The header depends on Linux endian definitions and ALSA/kernel integer types through the including driver headers. It is coupled to `dsp_spos.h` constants such as `SCBsubListPtr` and `SCBVolumeCtrl`, to firmware symbol names loaded by `cs46xx_dsp_load_module()`, and to constructor implementations in `dsp_spos_scb_lib.c`.

## Risks
The main risk is ABI drift: field order, padding, or offset changes can silently corrupt DSP execution. The structs are not explicitly packed, so maintainers must preserve naturally 32-bit-aligned layouts and avoid adding fields before fixed-offset members. Endian-sensitive paired 16-bit fields are another risk area. Many fields are hardware magic values with limited public documentation.

## Test signals
Useful signals are successful module load and `cs46xx_dsp_scb_and_task_init()`, no "symbol not found" or "failed to setup SCB's" logs, working playback/capture/SPDIF paths, valid `/proc/asound/.../dsp/scb_info` dumps when procfs is enabled, and suspend/resume restoring audio without stale links or muted SCBs.
