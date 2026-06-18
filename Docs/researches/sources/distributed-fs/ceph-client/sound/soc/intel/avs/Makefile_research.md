# sources/distributed-fs/ceph-client/sound/soc/intel/avs/Makefile

## Purpose
This Kbuild file defines the Intel AVS ASoC driver module and board subdirectory integration. It aggregates the generic AVS core, IPC, topology, path, PCM, loader, board-selection, control, sysfs, platform-specific DSP operations, trace support, and optional debugfs/probe support.

## Important APIs, types, and functions
`snd-soc-avs-y` includes common objects `dsp.o`, `ipc.o`, `messages.o`, `utils.o`, `core.o`, `loader.o`, `topology.o`, `path.o`, `pcm.o`, `board_selection.o`, `control.o`, and `sysfs.o`; CLDMA support `cldma.o`; platform variants `skl.o`, `apl.o`, `cnl.o`, `icl.o`, `tgl.o`, `mtl.o`, `lnl.o`, and `ptl.o`; and `trace.o`. `CFLAGS_trace.o := -I$(src)` supports `define_trace.h` include resolution. When `CONFIG_DEBUG_FS` is set, `probes.o` and `debugfs.o` are added. `obj-$(CONFIG_SND_SOC_INTEL_AVS)` builds `snd-soc-avs.o`, and `obj-$(CONFIG_SND_SOC) += boards/` enters machine support.

## Control flow
There is no runtime control flow. Build-time composition determines which platform-specific `avs_dsp_ops` objects and optional debug interfaces are linked into the AVS module.

## State and persistence behavior
The file has no runtime state. Its persistent effect is the Kbuild object graph.

## Dependencies and integration points
It depends on Kbuild, `CONFIG_SND_SOC_INTEL_AVS`, `CONFIG_DEBUG_FS`, and `CONFIG_SND_SOC`. The object list must stay aligned with prototypes in `avs.h` and with PCI platform descriptors in `core.c`.

## Risks and edge cases
Omitting a platform object breaks PCI IDs that reference its operation table. Omitting `trace.o` breaks tracepoint definitions; the special include flag is required for trace header generation. Debugfs objects must stay conditional on `CONFIG_DEBUG_FS`.

## Test signals
Build with AVS built-in and module, with and without debugfs, and with board support enabled. Check for unresolved symbols from platform operation tables, trace definitions, and debugfs/probe functions.
