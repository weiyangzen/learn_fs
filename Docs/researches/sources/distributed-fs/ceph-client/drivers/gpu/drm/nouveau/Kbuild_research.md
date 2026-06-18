# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/Kbuild

## Purpose
This Kbuild file defines how the Nouveau DRM driver is compiled. It assembles include paths and object lists for NVIF, NVKM, DRM integration, memory management, modesetting, and command submission.

## Important APIs, Types, And Data
It adds include directories for Nouveau public/internal headers and NVKM/GSP subtrees. It includes `nvif/Kbuild` and `nvkm/Kbuild`, then appends many objects to `nouveau-y`. Conditional objects depend on ACPI, debugfs, compat, LEDs, platform driver, SVM, and backlight configuration. It includes `dispnv04/Kbuild` and `dispnv50/Kbuild` for modesetting implementations and finally maps `obj-$(CONFIG_DRM_NOUVEAU)` to `nouveau.o`.

## Control Flow, State, And Integration
There is no runtime control flow. Build flow is modular: lower-level NVIF/NVKM object variables are included first, then the DRM-facing object list is extended. This file integrates the `dispnv04` files in this work item into the complete Nouveau module.

## Risks And Test Signals
Ordering and conditional symbol mismatches can produce missing symbols or dead code. Include path changes can affect both kernel and Nouveau-internal generated headers. Test signals are allmodconfig/allyesconfig builds, builds with optional features toggled, modpost with no unresolved symbols, and ensuring `dispnv04` objects are included when Nouveau is enabled.
