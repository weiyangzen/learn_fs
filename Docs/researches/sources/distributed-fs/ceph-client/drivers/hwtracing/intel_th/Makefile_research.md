# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/Makefile

## Purpose

`intel_th/Makefile` maps Intel Trace Hub Kconfig symbols to kernel objects and composite module contents.

## Important APIs, Types, and Functions

It builds `intel_th.o` from `core.o` plus optional `debug.o`. It builds glue modules `intel_th_pci.o` and `intel_th_acpi.o`, subdevice modules `intel_th_gth.o`, `intel_th_sth.o`, `intel_th_msu.o`, `intel_th_pti.o`, and `intel_th_msu_sink.o` from their corresponding source files.

## Control Flow

Kbuild includes each object according to `CONFIG_INTEL_TH*` symbols. Composite `*-y` assignments define which source files are linked into each module or built-in object.

## State and Persistence Behavior

There is no runtime state. Build state persists in generated objects according to Kconfig selections.

## Dependencies and Integration Points

This file integrates directly with `intel_th/Kconfig` and the Linux Kbuild system. `intel_th_msu_sink.o` is gated by `CONFIG_INTEL_TH_MSU`, so memory-storage sink support builds with MSU.

## Risks and Edge Cases

Object rules must stay synchronized with source filenames and Kconfig symbols. If a symbol is renamed or a source is moved, stale rules cause missing drivers or build failures.

## Test Signals

Build with each Intel TH config as built-in and module. Confirm optional debug object appears only with `CONFIG_INTEL_TH_DEBUG` and that MSU sink links when MSU is enabled.
