# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb/hal.rs

## Purpose

`fb/hal.rs` defines the framebuffer HAL trait and chipset dispatcher for sysmem flush page registers, display support detection, and VRAM size queries.

## Important APIs, Types, And Functions

`FbHal` exposes `read_sysmem_flush_page()`, `write_sysmem_flush_page()`, `supports_display()`, and `vidmem_size()`. `fb_hal(chipset)` returns a static HAL for Turing, GA100, or GA102/Ada families.

## Control Flow

Callers select the HAL through `fb_hal()`, then invoke trait methods when registering the sysmem flush page or computing `FbLayout`. Dispatch maps Turing chips to `tu102`, GA100 to `ga100`, and GA10x/Ada chips to `ga102`.

## State And Persistence Behavior

The dispatcher returns static trait-object references with no per-device state. Hardware state persists in registers written through concrete HALs.

## Dependencies And Integration Points

It depends on `Chipset`, BAR0 IO, and concrete HAL modules. It integrates with `SysmemFlush` and framebuffer layout computation.

## Risks And Test Signals

Risks include chipset dispatch drift, trait methods whose register formats differ by generation, and default assumptions for future GPUs. Test by querying HAL behavior for every `Chipset::ALL` variant, registering/unregistering sysmem flush pages, and comparing reported VRAM size/display status with hardware expectations.
