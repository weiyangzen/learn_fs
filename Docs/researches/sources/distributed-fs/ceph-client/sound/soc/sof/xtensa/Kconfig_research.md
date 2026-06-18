# sources/distributed-fs/ceph-client/sound/soc/sof/xtensa/Kconfig

Purpose: declares the hidden/tristate Kconfig symbol for SOF Xtensa DSP architecture support.

Important APIs/types: `config SND_SOC_SOF_XTENSA` is a tristate selected by platform drivers that need Xtensa oops/stack decoding.

Control flow/state: no runtime state. The symbol controls whether the `snd-sof-xtensa-dsp` module/object is built.

Dependencies/integration: used by SOF platform Kconfig entries for Xtensa-based DSPs.

Risks/test signals: build coverage should ensure platforms that reference `sof_xtensa_arch_ops` select this symbol and import the namespace correctly.
