# sources/distributed-fs/ceph-client/sound/hda/controllers/Makefile

## Purpose
This Makefile maps controller Kconfig symbols to loadable HD-audio controller objects and sets include paths needed by controller implementations.

## Important APIs, Types, and Functions
No runtime APIs are defined. Object groups are `snd-hda-intel-y`, `snd-hda-tegra-y`, `snd-hda-cix-ipbloq-y`, and `snd-hda-acpi-y`, each containing the matching single C file.

## Control Flow
`obj-$(CONFIG_...)` entries include the controller object in the build when the matching Kconfig symbol is enabled. `subdir-ccflags-y` adds `../common` headers, and `CFLAGS_intel.o := -I$(src)` lets Intel tracepoint generation include `intel_trace.h` via `TRACE_INCLUDE_PATH .`.

## State and Persistence Behavior
Build metadata only; no runtime state. It persists indirectly in generated build artifacts and module object names.

## Dependencies and Integration Points
The Makefile integrates controller sources with Kbuild, the common HDA controller helpers, and Linux tracepoint generation for the Intel driver.

## Risks
Changing object names or trace include flags can break module names or tracepoint header generation. Missing the common include path would break controller compilation against `hda_controller.h`.

## Test Signals
Build all four controller symbols as modules and built-ins, confirm generated module names, and verify `intel.o` compiles with `CREATE_TRACE_POINTS` and `intel_trace.h`.
