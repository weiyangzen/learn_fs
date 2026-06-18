# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/Makefile

Purpose: Kbuild fragment for the Intel CATPT ASoC driver object.

Important APIs, types, and functions: It defines `snd-soc-catpt-y` as the object list `device.o dsp.o loader.o ipc.o messages.o pcm.o sysfs.o`, adds `CFLAGS_device.o := -I$(src)` so `define_trace.h` can locate the trace header relative to the source directory, and builds `snd-soc-catpt.o` when `CONFIG_SND_SOC_INTEL_CATPT` is enabled.

Control flow and integration: Kernel Kbuild includes this Makefile from the Intel ASoC subtree. The composite object links the CATPT driver modules into one loadable/built-in object controlled by the Kconfig symbol.

State and persistence: Build metadata only. No runtime state.

Dependencies: Kbuild composite object syntax, the listed CATPT source files, and `CONFIG_SND_SOC_INTEL_CATPT`.

Risks: Missing `-I$(src)` can break trace header inclusion in `device.o`. Object list omissions cause link-time or runtime feature gaps. Test signals include kernel build with CATPT enabled as module and built-in, trace header compilation, and expected `snd-soc-catpt` object contents.
