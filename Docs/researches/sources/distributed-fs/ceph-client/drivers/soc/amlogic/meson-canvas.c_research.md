# sources/distributed-fs/ceph-client/drivers/soc/amlogic/meson-canvas.c

## Purpose
This driver manages the Amlogic Meson canvas hardware lookup table, which maps small canvas IDs to physical buffer layout parameters used by display/video blocks.

## Important APIs, Types, And Functions
The core state is `struct meson_canvas`, containing MMIO base, spinlock, 256-entry allocation bitmap, and endianness support. Exported APIs are `meson_canvas_get()`, `meson_canvas_alloc()`, `meson_canvas_config()`, and `meson_canvas_free()`. `canvas_write()` and `canvas_read()` are local MMIO helpers.

## Control Flow
Consumers obtain a canvas provider through the `amlogic,canvas` phandle. Allocation scans `used[]` for a free ID under the lock. Configuration checks endianness support and allocation state, writes low and high layout registers, triggers a LUT write for the selected index, and reads back to flush writes. Free clears the allocation state.

## State, Persistence, And Dependencies
State is runtime-only in `used[]` and hardware LUT registers. The driver depends on platform resource mapping, device tree matching, MMIO, spinlocks, and the public Amlogic canvas header.

## Integration Points
Video, DRM, and media drivers call exported functions to allocate and configure canvas IDs. The provider is matched by compatibles including legacy Meson8 variants and generic `amlogic,canvas`.

## Risks
The API trusts `canvas_index` bounds because it is a `u8`, matching `NUM_CANVAS`. Address/stride/height fields are packed with rounding but not range-checked against bit widths. Consumers must free IDs or leaks persist until driver removal. `meson_canvas_get()` returns `-EINVAL` if provider drvdata is not set instead of deferring.

## Test Signals
Probe on each compatible, allocate all 256 IDs, verify exhaustion, configure an allocated ID, reject unallocated config/free, reject endianness on older SoCs, and validate downstream display/video behavior.
