
# sources/distributed-fs/ceph-client/sound/pci/oxygen/Makefile

Purpose: kernel Kbuild manifest for the Oxygen/CMI878x ALSA PCI driver family. It builds `snd-oxygen-lib` from shared bus, PCI, mixer, and PCM code; `snd-oxygen` from the C-Media reference/Xonar DG entry code; `snd-se6x` for Studio Evolution SE6X; and `snd-virtuoso` for Asus Xonar Virtuoso boards.

Important APIs and integration points: the file maps `CONFIG_SND_OXYGEN_LIB`, `CONFIG_SND_OXYGEN`, `CONFIG_SND_SE6X`, and `CONFIG_SND_VIRTUOSO` to loadable objects. The Virtuoso object explicitly pulls `xonar_lib.o`, PCM179x, CS43xx, WM87x6, and HDMI support, while `snd-oxygen` includes `xonar_dg_mixer.o` and `xonar_dg.o`.

Control flow/state: no runtime state, but link composition controls which `oxygen_model` providers are present in each module. Dependency risks are mostly missing object linkage: moving a board callback without updating this file causes unresolved symbols or unsupported PCI IDs. Test signals are kernel build coverage for all four configs and module load/probe smoke tests.
