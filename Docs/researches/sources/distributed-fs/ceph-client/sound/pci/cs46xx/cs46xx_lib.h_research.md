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
