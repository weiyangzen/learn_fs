# sources/distributed-fs/ceph-client/sound/soc/sof/intel/nvl.c

Purpose: adds Nova Lake chip descriptors and ops binding for SOF HDA. It reuses Panther Lake ops while supplying NVL/NVL-S core counts and ACE4 descriptor metadata.

Important APIs: `sof_nvl_set_ops()` delegates directly to `sof_ptl_set_ops()`. `nvl_chip_info` and `nvl_s_chip_info` define four-core and two-core variants with ACE4 IP version, LNL ROM status register, MTL IPC registers, extended SoundWire lcount, LNL SDW/wake/interrupt callbacks, MTL boot/power helpers, and platform string `nvl`.

Control flow: PCI NVL descriptors call `sof_nvl_set_ops()` during probe, causing PTL-derived ops to be installed while `hda.c` uses the NVL chip descriptor for register offsets and feature decisions.

State and persistence: no private state; runtime state is inherited from HDA/MTL/PTL paths.

Dependencies and integration: depends on MTL, LNL, PTL, HDA common, IPC4, and multi-link/SoundWire definitions.

Risks and test signals: risks include assuming PTL ops fully match NVL, descriptor copy/paste errors between NVL and NVL-S, and ACE4-specific stream alignment/BT topology paths. Test both PCI IDs, firmware path selection, SoundWire, PM, IPC, dspless mode, and core count behavior.
