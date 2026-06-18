# sources/distributed-fs/ceph-client/sound/soc/sof/Makefile

Purpose: object composition for the SOF core module, enumeration modules, clients, nocodec, utility object, and vendor subdirectories.

Important APIs/types/functions: `snd-sof-y` gathers core objects (`core.o`, `ops.o`, `loader.o`, `ipc.o`, `pcm.o`, `pm.o`, `debug.o`, `topology.o`, `control.o`, trace/audio/stream helpers, and `fw-file-profile.o`). IPC3 and IPC4 object lists are conditional. Client modules include IPC flood test, message injectors, kernel injector, and probes. Enumeration modules are `snd-sof-pci`, `snd-sof-acpi`, and `snd-sof-of`.

Control flow: Kconfig symbols decide which object lists are appended and which modules are emitted under `obj-*`. Vendor subdirectories are descended into through toplevel symbols.

State and persistence: build-time only; no runtime state.

Dependencies and integration points: ties the symbols from `Kconfig` to compiled driver code. The AMD and i.MX files in this research rely on the vendor subdir entries and shared `snd-sof.o`.

Risks: IPC object lists are conditionally appended with `ifneq ($(CONFIG_*),)`, so mixed built-in/module combinations need correct symbol propagation. Missing an object from `snd-sof-y` can break a shared exported callback without an obvious source-level error.

Test signals: kernel allmodconfig/allyesconfig and targeted SOF platform builds validate object coverage.
