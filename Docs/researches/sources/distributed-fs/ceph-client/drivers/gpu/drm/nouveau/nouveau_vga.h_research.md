# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_vga.h

## Purpose
This small header declares Nouveau VGA/switcheroo lifecycle hooks.

## Important APIs, Types, and Functions
It exposes `nouveau_vga_init` and `nouveau_vga_fini`.

## Control Flow
No executable flow exists in the header. Driver load/unload code calls these hooks around PCI VGA arbiter and switcheroo registration.

## State and Persistence Behavior
The header stores no state. The implementation mutates VGA arbiter registration, switcheroo registration, and optional runtime PM domain state.

## Dependencies and Integration Points
It is included by Nouveau driver initialization code and depends on `struct nouveau_drm` being visible to callers.

## Risks
The risk is signature drift or forgotten fini calls, which would leave VGA/switcheroo registrations active after device removal.

## Test Signals
Build coverage and PCI driver load/unload on VGA-capable systems validate the interface.
