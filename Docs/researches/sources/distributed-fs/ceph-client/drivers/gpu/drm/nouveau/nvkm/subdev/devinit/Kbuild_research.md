# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/Kbuild

## Purpose
Builds the Nouveau devinit subdevice objects for legacy through modern GPU generations, including the R535 GSP-backed wrapper.

## Important APIs, types, and functions
The file lists `nvkm-y` object inclusions for base, generation-specific devinit files, and `r535.o`.

## Control flow
Kbuild has no runtime flow; it controls which translation units are linked into the NVKM module.

## State and persistence
No runtime state. Build state is the linked object set.

## Dependencies and integration points
Integrated by the parent Nouveau Kbuild. The object list must match constructor references in the device chipset table.

## Risks
Missing a generation object causes unresolved symbols or absent support for a chipset. Keeping `r535.o` linked is required for GSP RM paths in TU102/GA100.

## Test signals
Kernel build/link coverage and modpost symbol resolution for every devinit constructor.
