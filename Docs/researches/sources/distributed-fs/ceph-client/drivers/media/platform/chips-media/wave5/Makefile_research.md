# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/Makefile

## Purpose
`wave5/Makefile` defines how the Wave5 driver is linked. It produces one composite object, `wave5.o`, when `CONFIG_VIDEO_WAVE_VPU` is enabled.

## Important Build Entries
The build target is `obj-$(CONFIG_VIDEO_WAVE_VPU) += wave5.o`. The composite object includes `wave5-hw.o`, `wave5-vpuapi.o`, `wave5-vdi.o`, `wave5-vpu-dec.o`, `wave5-vpu.o`, `wave5-vpu-enc.o`, and `wave5-helper.o`.

## Control Flow and Integration
There is no runtime control flow. Build integration ensures low-level hardware access, API wrappers, VDI memory/MMIO helpers, decoder frontend, platform device logic, encoder frontend, and shared helpers are linked into the same module or built-in object. This matters because many functions are cross-file internal driver APIs rather than separately exported module symbols.

## State and Persistence
The Makefile only controls build artifacts. Its persistent effect is the object composition used by the kernel build system.

## Dependencies and Risks
The Makefile depends on object names matching source files. Adding or removing Wave5 source files requires updating this list. A missing object can produce unresolved symbols, while stale entries break builds. The current list includes both decoder and encoder paths, matching the shared Kconfig description.

## Test Signals
Run kernel builds with `CONFIG_VIDEO_WAVE_VPU=y` and `m`, check that `wave5.o` or `wave5.ko` links without unresolved symbols, and verify incremental builds notice edits across all listed source files.
