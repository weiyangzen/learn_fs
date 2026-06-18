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
