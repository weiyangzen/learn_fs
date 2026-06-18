# sources/distributed-fs/ceph-client/sound/soc/sof/xtensa/Makefile

Purpose: builds the SOF Xtensa DSP support object.

Important APIs/types: `snd-sof-xtensa-dsp-y := core.o` and `obj-$(CONFIG_SND_SOC_SOF_XTENSA) += snd-sof-xtensa-dsp.o`.

Control flow/state: no runtime state; build output is controlled by `CONFIG_SND_SOC_SOF_XTENSA`.

Dependencies/integration: integrates `xtensa/core.c` into the kernel/module build when selected.

Risks/test signals: module namespace export should be verified by building SOF platform modules that consume `sof_xtensa_arch_ops` as modules and built-ins.
