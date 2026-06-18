# sources/distributed-fs/ceph-client/sound/soc/sof/intel/lnl.h

Purpose: declares Lunar Lake-specific register offsets and exported helper prototypes used by LNL/NVL/PTL-adjacent SOF HDA code.

Important APIs/types: defines `LNL_DSP_REG_HFDSC` and `LNL_DSP_REG_HFDEC` for DSP core0 status/error, plus prototypes for `sof_lnl_set_ops()`, `lnl_dsp_check_sdw_irq()`, `lnl_dsp_disable_interrupts()`, and `lnl_sdw_check_wakeen_irq()`.

Control flow: no runtime logic; it enables PCI/platform files and later-generation descriptors to reuse LNL SoundWire and interrupt helpers.

State and persistence: none.

Dependencies and integration: consumed by `lnl.c` and `nvl.c`; relies on `struct snd_sof_dev` and `struct snd_sof_dsp_ops` declarations from included compilation units.

Risks and test signals: risks are limited to register offset drift and prototype mismatches. Build all LNL/NVL/PTL modules and verify ROM status/error dumps use the expected addresses.
