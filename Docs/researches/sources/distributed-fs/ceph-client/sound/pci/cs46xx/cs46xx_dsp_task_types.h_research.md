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
