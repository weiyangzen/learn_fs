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
