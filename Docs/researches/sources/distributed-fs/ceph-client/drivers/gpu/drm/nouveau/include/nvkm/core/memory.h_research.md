# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/memory.h

## Purpose

This header defines the polymorphic NVKM memory object used for instance memory, VRAM, host coherent memory, and non-coherent host allocations. It provides reference counting, compression-tag accounting, mapping hooks, and register-style access helpers.

## Important APIs, Types, and Functions

Important contracts include `enum nvkm_memory_target`, `struct nvkm_memory`, `struct nvkm_memory_func`, `struct nvkm_memory_ptrs`, `struct nvkm_tags`, `nvkm_memory_new`, `nvkm_memory_ref`, `nvkm_memory_unref`, `nvkm_memory_tags_get`, `nvkm_memory_tags_put`, and access macros such as `nvkm_kmap`, `nvkm_done`, `nvkm_ro32`, `nvkm_wo32`, `nvkm_mo32`, `nvkm_robj`, `nvkm_wobj`, `nvkm_fo32`, and `nvkm_fo64`.

## Control Flow

Backends construct a memory object with function tables, callers map or kmap it through backend hooks, perform 32/64-bit access or bulk fill/copy, and release mappings before dropping references. VMM mapping routes through the `map` hook, while compression tags are leased and returned through the tag helpers.

## State and Persistence Behavior

The base object persists target type, page geometry, physical/BAR addresses supplied by callbacks, krefs, and optional compression tag references. The underlying memory can represent durable VRAM contents or transient instance memory that may be lost across suspend.

## Dependencies and Integration Points

It is used by GPU objects, firmware wrappers, VMM mappings, framebuffer tag allocation, RAM wrappers, and engine context storage. Correct acquire/release pairing is required because some backends expose I/O memory only while mapped.

## Risks

Using access macros outside `kmap`/`done` semantics can break on chipsets with special mapping requirements. Tag reference leaks affect compression resources. Wrong target/page reporting causes invalid PTE programming and data coherency bugs.

## Test Signals

Validate refcounting, kmap fallback paths, BAR2/addr/size reporting, memory fill/copy helpers, VMM map/unmap, compression-tag get/put, and suspend behavior for `INST_SR_LOST` versus preserved targets.
