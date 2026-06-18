# sources/distributed-fs/ceph-client/sound/soc/intel/atom/Makefile

Purpose: kbuild file for Intel Atom HiFi2 SST platform support.

Important APIs/types/functions: defines composite object `snd-soc-sst-atom-hifi2-platform-y` from `sst-mfld-platform-pcm.o`, `sst-mfld-platform-compress.o`, and `sst-atom-controls.o`; includes that composite and the `sst/` DSP subdirectory when `CONFIG_SND_SST_ATOM_HIFI2_PLATFORM` is enabled.

Control flow: selecting the hidden base Atom HiFi2 platform symbol builds both PCM/compress/control support and the DSP driver subtree.

State and persistence: build-time only.

Dependencies/integration: driven by `SND_SST_ATOM_HIFI2_PLATFORM`, selected by PCI and ACPI variants in Intel Kconfig.

Risks: the composite object and `sst/` subtree are controlled by the same symbol, so partial builds are not possible through Kconfig. Source file names must remain aligned with legacy Merrifield/Baytrail/Cherrytrail support.

Test signals: module/built-in builds for Atom PCI and ACPI options should produce `snd-soc-sst-atom-hifi2-platform` and recurse into `atom/sst/`.
