# subset-b-006390 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx_dsp_scb_types.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx_dsp_scb_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx_dsp_spos.h -->
# sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx_dsp_spos.h

## Purpose
`cs46xx_dsp_spos.h` defines the high-level in-kernel model of the new CS46xx DSP SPOS runtime. It is the shared contract for firmware modules, symbols, SCB descriptors, task descriptors, PCM channel descriptors, SPDIF state, mixer SCBs, and capture source state. Unlike `dsp_spos.h`, which is mostly constants and inline register helpers, this header describes the driver's persistent software graph for objects already loaded into DSP memory.

## Important APIs and types
It defines symbol kinds (`SYMBOL_CONSTANT`, `SYMBOL_SAMPLE`, `SYMBOL_PARAMETER`, `SYMBOL_CODE`) and firmware segment kinds (`SEGTYPE_SP_PROGRAM`, `SEGTYPE_SP_PARAMETER`, `SEGTYPE_SP_SAMPLE`, `SEGTYPE_SP_COEFFICIENT`). It also defines sentinel constants such as `DSP_SPOS_UU`, `DSP_SPOS_DC`, and variants used when building SCB/task blocks. Main types are `dsp_symbol_entry`, `dsp_symbol_desc`, `dsp_segment_desc`, `dsp_module_desc`, `dsp_scb_descriptor`, `dsp_task_descriptor`, `dsp_pcm_channel_descriptor`, and `dsp_spos_instance`.

## Control flow and state
`dsp_spos_instance` is created by `cs46xx_dsp_spos_create()` during device creation and destroyed in card teardown. It tracks loaded firmware modules, relocated code shadow data, a symbol table, all mapped SCBs/tasks, active PCM channels, SRC slots, mixer roots, SPDIF state bits, IEC958 channel status words, and record source pointers. Runtime functions in `dsp_spos.c`, `dsp_spos_scb_lib.c`, and `cs46xx_lib.c` mutate this instance while holding `chip->spos_mutex` for graph-level changes.

## Persistence behavior
Most fields mirror volatile hardware/DSP state. The module list, shadow code segment, task descriptors, SCB descriptors, volume cache, SPDIF status, and saved SCB data enable reconstruction after suspend/resume. PCM channel descriptors are runtime allocations and are linked/unlinked from SCB lists according to ALSA trigger/open/close state.

## Dependencies and integration points
The header includes SCB and task layout headers and is pulled in through `cs46xx.h` or `cs46xx_lib.h`. It integrates with firmware loading in `cs46xx_lib.c`, SCB graph construction in `dsp_spos.c`, detailed SCB constructors in `dsp_spos_scb_lib.c`, ALSA PCM/mixer controls, procfs diagnostics, and PM resume.

## Risks
The header centralizes many fixed limits: `DSP_MAX_SYMBOLS`, `DSP_MAX_MODULES`, `DSP_MAX_PCM_CHANNELS`, `DSP_MAX_SRC_NR`, `DSP_MAX_SCB_DESC`, and `DSP_MAX_TASK_DESC`. Overflow handling exists but is sparse. Pointer fields inside descriptors must remain consistent with DSP memory links. SPDIF state is split between `spdif_status_out` and `spdif_status_in`, so control code must avoid stale status across open/close and suspend/resume.

## Test signals
Good signals include clean SPOS allocation/destruction under memory pressure, no symbol/SCB descriptor leaks after repeated PCM opens, stable `/proc` symbol/module/task/SCB dumps, correct multichannel PCM device behavior, SPDIF controls preserving channel status, and resume restoring DAC/SPDIF volumes and graph links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx_dsp_spos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx_dsp_task_types.h -->
# sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx_dsp_task_types.h

## Purpose
`cs46xx_dsp_task_types.h` defines the DSP task tree control structures used by the CS46xx SPOS scheduler. It is layout-only support code for the new DSP path and documents how hyper-foreground, foreground, middle/background-style trees, context saves, stack bases, timer data, active flags, and tree links are represented in DSP parameter memory.

## Important APIs and types
The file defines task execution flags (`HFG_FIRST_EXECUTE_MODE`, `HFG_CONTEXT_SWITCH_MODE`), stack-size constants, active increment modes (`SLEEP_ACTIVE_INCREMENT`, `STANDARD_ACTIVE_INCREMENT`, `SUSPEND_ACTIVE_INCREMENT`), and `HOSTFLAGS_DISABLE_BG_SLEEP`. Layouts include `dsp_hf_save_area`, `dsp_tree_link`, `dsp_task_tree_data`, `dsp_interval_timer_data`, `dsp_task_tree_context_block`, and the aggregate `dsp_task_tree_control_block`.

## Control flow and integration
`dsp_spos.c` constructs `dsp_task_tree_control_block` instances for the foreground and background task trees in `cs46xx_dsp_scb_and_task_init()`. The host writes these blocks into DSP parameter memory with `cs46xx_dsp_create_task_tree()`. Firmware symbols such as `FGTASKTREEHEADERCODE`, `TASKTREEHEADERCODE`, and `TASKTREETHREAD` provide entry points that make the block executable by the DSP scheduler.

## State and persistence behavior
The structures hold scheduler state in DSP memory. Some fields are host-initialized and then treated as DSP-owned context, counters, active flags, and save areas. `cs46xx_dsp_resume()` rewrites task descriptor data after reset, making the initial task tree layouts persistent across PM cycles through the software `dsp_task_descriptor` cache.

## Dependencies and integration points
The file depends on `cs46xx_dsp_scb_types.h` only for the endian-aware dual 16-bit allocation macro. It is consumed by `cs46xx_dsp_spos.h` and `dsp_spos.c` and is indirectly coupled to the firmware symbol table loaded from `cs46xx/cwc*` firmware files.

## Risks
The main risk is corrupting scheduler context by changing field order or sizes. Many comments warn that stack sizes should be computed properly, so hard-coded limits may be fragile. Host and DSP ownership of fields is implicit; writing a DSP-owned field at runtime could cause scheduler instability. Test coverage should especially protect foreground/background task tree initialization and resume rewrite.

## Test signals
Signals include successful `cs46xx_dsp_scb_and_task_init()`, the DSP leaving reset and clearing `SPCR_RUNFR`, no trap/spurious interrupt flags in SPOS control data, stable playback/capture interrupts, and valid task tree dumps from `cs46xx_dsp_proc_task_tree_read()` when procfs support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx_dsp_task_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx_lib.c -->
# sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx_lib.c

## Purpose
`cs46xx_lib.c` is the main ALSA support library for Cirrus Logic CS461x/CS46xx cards. It owns PCI resource mapping, chip initialization, AC97 access, firmware loading, DSP startup, PCM devices, mixer controls, raw MIDI, optional gameport/proc interfaces, board-specific amplifier/CLKRUN quirks, interrupt handling, power management, and final card teardown. It supports both the legacy monolithic BA1 firmware path and the `CONFIG_SND_CS46XX_NEW_DSP` modular SPOS path.

## Important APIs and functions
Exported or externally called entry points include `snd_cs46xx_create()`, `snd_cs46xx_start_dsp()`, `snd_cs46xx_pcm()`, `snd_cs46xx_pcm_rear()`, `snd_cs46xx_pcm_center_lfe()`, `snd_cs46xx_pcm_iec958()`, `snd_cs46xx_mixer()`, `snd_cs46xx_midi()`, `snd_cs46xx_gameport()`, `snd_cs46xx_download()`, and, for the new DSP path, `snd_cs46xx_clear_BA1()`. Internal pillars include AC97 read/write helpers, firmware parsers, reset/start/stop helpers, sample-rate calculators, PCM open/prepare/hw_params/trigger/pointer methods, mixer control callbacks, MIDI triggers, procfs IO mapping, card quirk handlers, suspend/resume, and IRQ demux.

## Control flow
Probe code in `cs46xx.c` calls `snd_cs46xx_create()` to enable PCI, request regions, map BA0/BA1 windows, install IRQ, create a SPOS instance when configured, initialize the chip, and register proc entries. Later `snd_cs46xx_mixer()` creates AC97 bus/codecs and mixer controls, PCM helper functions create ALSA devices, and `snd_cs46xx_start_dsp()` resets the processor, loads firmware, initializes SCBs/tasks for the new DSP path or downloads the legacy image, starts the processor, and enables stream interrupts. PCM trigger paths link/unlink DSP PCM SCBs for playback and toggle capture DMA. The interrupt handler clears device IRQ state, reports PCM period elapsed events, services MIDI RX/TX, and re-enables PCI interrupts.

## State and persistence behavior
State lives in `struct snd_cs46xx`: mapped memory regions, AC97 bus/codecs, IRQ, PCM and capture buffers, mixer callbacks, active/amplifier counters, MIDI state, DSP modules, SPOS instance, saved PM registers, and optional gameport. Runtime DMA buffers are allocated per open or preallocated for devices. Suspend saves selected registers, suspends AC97, powers down amplifier and hardware; resume reinitializes the chip, reloads DSP/firmware state, restores registers, AC97, sample rates, proc start, IRQs, and amplifier state.

## Dependencies and integration points
The file integrates heavily with ALSA core, PCM, control, rawmidi, AC97, procfs, Linux PCI, firmware loader, IRQ, PM, gameport, and MMIO APIs. It includes `cs46xx.h`, `cs46xx_lib.h`, and `dsp_spos.h`; new DSP behavior depends on `dsp_spos.c` and `dsp_spos_scb_lib.c` for SCB graph management.

## Risks
Risk clusters are hardware timing loops, unchecked firmware format assumptions, fragile magic constants for SPDIF/AC97/board quirks, race-sensitive register access split between `reg_lock` and `spos_mutex`, and the dual legacy/new DSP compile-time paths. Some known bugs are documented in the file, especially SPDIF input desynchronization and Hercules amplifier glitches. PCM paths switch ops dynamically based on period count, so buffer ownership must remain exact.

## Test signals
High-value tests are device probe/remove, firmware load failures, AC97 primary/secondary detection, playback/capture at varied rates/formats/period counts, indirect-buffer transfers, MIDI duplex operation, mixer control get/put behavior, SPDIF output/input toggles and IEC958 status updates, interrupt period accounting, board quirk paths, procfs reads, and suspend/resume with active PCM/SPDIF states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx_lib.h -->
# sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx_lib.h

## Purpose
`cs46xx_lib.h` is the internal interface between the CS46xx ALSA core, low-level MMIO helpers, and the new DSP/SPOS support code. It defines BA0/BA1 window sizes, PCM period limits, SCB parent-link modes, BA1 memory sizing, inline register accessors, and prototypes for DSP, PCM, SPDIF, record-source, and volume functions used across `cs46xx_lib.c`, `dsp_spos.c`, and `dsp_spos_scb_lib.c`.

## Important APIs and constants
Constants describe mapped hardware windows (`CS46XX_BA0_SIZE`, `CS46XX_BA1_DATA0_SIZE`, `CS46XX_BA1_DATA1_SIZE`, `CS46XX_BA1_PRG_SIZE`, `CS46XX_BA1_REG_SIZE`), period sizes (`CS46XX_MIN_PERIOD_SIZE`, `CS46XX_MAX_PERIOD_SIZE`, `CS46XX_FRAGS`), SCB placement (`SCB_NO_PARENT`, `SCB_ON_PARENT_NEXT_SCB`, `SCB_ON_PARENT_SUBLIST_SCB`), and legacy BA1 image dimensions. Inline accessors are `snd_cs46xx_poke()`, `snd_cs46xx_peek()`, `snd_cs46xx_pokeBA0()`, and `snd_cs46xx_peekBA0()`.

## Control flow and integration
The inline accessors split a logical BA1 register address into bank and offset and use `chip->region.idx[bank+1].remap_addr`; BA0 helpers use `chip->region.name.ba0`. Function prototypes expose SPOS lifecycle, firmware/module loading, proc hooks, SCB/task initialization, raw BA1 download/clear helpers, SPDIF input/output controls, PCM channel creation/destruction/linking, record source insertion, period programming, and DSP volume setters.

## State and persistence behavior
The header has no storage, but its APIs mutate persistent device state through `struct snd_cs46xx` and `struct dsp_spos_instance`. The `CONFIG_PM_SLEEP` and `CONFIG_SND_PROC_FS` blocks define whether resume/proc helpers are real calls or no-op macros. Period-size constants alter ALSA runtime constraints between legacy and new DSP builds.

## Dependencies and integration points
The header assumes `struct snd_cs46xx`, `struct dsp_module_desc`, `struct dsp_scb_descriptor`, and related types are visible from included driver headers. It is included by both ALSA-facing code and DSP code, so it is a narrow but high-impact contract. It also indirectly depends on Linux MMIO semantics through `readl()`/`writel()`.

## Risks
Incorrect bank calculation in `snd_cs46xx_poke/peek()` or mismatched region indexing would corrupt the wrong BA1 area. The duplicate `cs46xx_dsp_create_codec_in_scb()` prototype is harmless but signals hand-maintained API drift. Compile-time no-op macros for proc support can hide missing diagnostics. Any prototype mismatch with `dsp_spos_scb_lib.c` will break the new DSP path.

## Test signals
Build both legacy and `CONFIG_SND_CS46XX_NEW_DSP` configurations, with and without procfs and PM. Exercise BA0/BA1 register access through probe, firmware download, PCM prepare/trigger, SPDIF toggles, proc dumps, and resume. Static analysis should check prototype consistency and address arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/dsp_spos.c -->
# sources/distributed-fs/ceph-client/sound/pci/cs46xx/dsp_spos.c

## Purpose
`dsp_spos.c` implements the SPOS runtime manager for the `CONFIG_SND_CS46XX_NEW_DSP` path. It allocates and destroys the software SPOS instance, loads modular firmware segments into DSP memory, relocates wide instructions and symbols, maps SCBs and task trees, creates the baseline DSP execution graph, registers procfs diagnostics, controls SPDIF input/hardware state, inserts/removes capture sources, performs DSP IO pokes through a helper SCB, manages DSP volume caches, and restores DSP state after suspend.

## Important APIs and functions
Key external functions are `cs46xx_dsp_spos_create()`, `cs46xx_dsp_spos_destroy()`, `cs46xx_dsp_load_module()`, `cs46xx_dsp_lookup_symbol()`, `cs46xx_dsp_proc_init()`, `cs46xx_dsp_proc_done()`, `cs46xx_dsp_create_scb()`, `cs46xx_dsp_scb_and_task_init()`, `cs46xx_dsp_enable_spdif_hw()`, `cs46xx_dsp_enable_spdif_in()`, `cs46xx_dsp_disable_spdif_in()`, `cs46xx_dsp_enable_pcm_capture()`, `cs46xx_dsp_disable_pcm_capture()`, `cs46xx_dsp_enable_adc_capture()`, `cs46xx_dsp_disable_adc_capture()`, `cs46xx_poke_via_dsp()`, `cs46xx_dsp_set_dac_volume()`, `cs46xx_dsp_set_iec958_volume()`, and `cs46xx_dsp_resume()`.

## Control flow
Firmware load goes through `cs46xx_dsp_load_module()`: clear BA1 areas on the first module, download parameter/sample segments, relocate code using `shadow_and_reallocate_code()`, add adjusted symbols, download code, and cache module metadata. SPOS graph initialization creates `sposCB`, null SCB, foreground/background task trees, timing master, codec out/in, master/rear/center-LFE mixers, writeback, vari-decimate capture path, magic snoop, SPIO writer, SPDIF SRC, and async SPDIF/input foreground SCBs. SPDIF input later creates an async receiver, links the SRC, unmutes it, and toggles SP-only registers through `cs46xx_poke_via_dsp()`.

## State and persistence behavior
`dsp_spos_instance` owns symbol/module/code/SCB/task caches plus mixer, PCM, record, and SPDIF state. SCB descriptors track software links, parentage, proc entries, deleted/reused slots, runtime volume, and whether link/volume writes need replay on resume. PM resume clears BA1 areas, reloads all module segments from cached data, rewrites task trees and SCBs, reapplies updated links and volumes, and restores SPDIF hardware/input state.

## Dependencies and integration points
The file depends on firmware module descriptors parsed by `cs46xx_lib.c`, hardware memory windows from `snd_cs46xx_download()`/`snd_cs46xx_clear_BA1()`, constants and inline helpers from `dsp_spos.h`, layouts from the SCB/task headers, ALSA procfs, and constructor/link helpers implemented in `dsp_spos_scb_lib.c`.

## Risks
Relocation is fragile: `shadow_and_reallocate_code()` recognizes a fixed set of wide opcodes and adjusts non-ROM addresses based on overlay symbols. Symbol duplication is mostly ignored for firmware symbols but rejected for driver-added symbols. SCB allocation reuses deleted slots and must keep symbol table deletion in sync. `cs46xx_poke_via_dsp()` relies on the SPIOWrite task responding within a polling window. Several SPDIF constants are documented as magic and only 48 kHz input is supported.

## Test signals
Test module loading for all `cwc*` firmware files, missing symbol failures, procfs symbol/module/task/SCB dumps, playback graph creation on one-codec and two-codec cards, SPDIF input toggling, PCM/ADC capture switches, DSP poke timeout handling, repeated create/remove of dynamic SCBs, and suspend/resume with previously linked PCM/SPDIF paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/dsp_spos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/dsp_spos.h -->
# sources/distributed-fs/ceph-client/sound/pci/cs46xx/dsp_spos.h

## Purpose
`dsp_spos.h` is the low-level constants and inline-helper header for the CS46xx new DSP SPOS path. It is compiled only under `CONFIG_SND_CS46XX_NEW_DSP` and supplies DSP memory sizes, memory offsets, relocation opcode identifiers, fixed sample-buffer/task/SCB addresses, SCB field offsets, stream configuration bit masks, SP-only register addresses, channel-status bit wrapping, and direct SCB patch helpers.

## Important APIs and constants
The header defines DSP memory areas (`DSP_CODE_BYTE_SIZE`, `DSP_PARAMETER_BYTE_SIZE`, `DSP_SAMPLE_BYTE_SIZE` and offsets), relocation masks/opcodes (`WIDE_INSTR_MASK`, `WIDE_LADD_INSTR_MASK`, `enum wide_opcode`), sample buffer addresses (`PCM_READER_BUF1`, `MIX_SAMPLE_BUF*`, SPDIF buffers, snoop buffers), SCB/task addresses (`SPOSCB_ADDR`, `TIMINGMASTER_SCB_ADDR`, `MASTERMIX_SCB_ADDR`, `HFG_TREE_SCB`, etc.), field offsets (`SCBsubListPtr`, `SCBfuncEntryPtr`, `SCBVolumeCtrl`), stream config flags (`RSCONFIG_*`), and SP register addresses (`SP_SPDOUT_CONTROL`, `SP_SPDIN_CONTROL`, `SP_SPDOUT_CSUV`, and related FIFO/status registers).

## Control flow and helpers
`_wrap_all_bits()` reverses bit order in a byte for IEC958 channel-status representation. `cs46xx_dsp_spos_update_scb()` patches an existing SCB's `sub_list_ptr` and `next_scb` dword in DSP memory and marks the descriptor updated for resume replay. `cs46xx_dsp_scb_set_volume()` writes inverted left/right target/current volume values to the two volume-control dwords and caches the requested values in the descriptor.

## State and persistence behavior
The header itself stores no state, but its helpers mutate both DSP memory and `dsp_scb_descriptor` flags (`updated`, `volume_set`, `volume[]`). Those flags are consumed by `cs46xx_dsp_resume()` to restore runtime changes after BA1 memory is cleared and rewritten.

## Dependencies and integration points
The helpers require `struct snd_cs46xx`, `struct dsp_scb_descriptor`, and `snd_cs46xx_poke()` from the broader driver. The constants are used by `dsp_spos.c`, `dsp_spos_scb_lib.c`, and `cs46xx_lib.c` for SCB construction, PCM pointer reads, period programming, SPDIF controls, and proc dumps.

## Risks
Address and offset constants are hardware/firmware ABI. A wrong constant can redirect DSP task links, corrupt sample buffers, or poke an SP register through the wrong route. Volume writes invert ALSA-style values with `0xffff - value`, so callers must pass the expected range. `cs46xx_dsp_spos_update_scb()` assumes both link pointers are non-null and valid descriptor addresses.

## Test signals
Useful signals include correct PCM pointer progression from SCB address reads, working runtime SCB link/unlink operations, volume changes surviving resume, IEC958 channel-status bytes matching ALSA controls after bit wrapping, SPDIF input/output control register effects, and no DSP graph corruption in procfs SCB dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/dsp_spos.h -->
