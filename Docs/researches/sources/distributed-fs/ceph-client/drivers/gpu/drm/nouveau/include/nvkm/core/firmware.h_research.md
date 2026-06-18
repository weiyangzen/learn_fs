# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/firmware.h

## Purpose

This header defines the NVKM firmware blob wrapper used to represent firmware stored in kernel RAM, DMA memory, or scatter-gather tables, plus helpers for locating versioned firmware files and selecting firmware loader variants from module options.

## Important APIs, Types, and Functions

Key elements are `struct nvkm_firmware`, `struct nvkm_firmware_func`, `enum nvkm_firmware_type`, `struct nvkm_firmware_mem`, `nvkm_firmware_ctor`, `nvkm_firmware_dtor`, `nvkm_firmware_get`, `nvkm_firmware_put`, `nvkm_firmware_load_blob`, `nvkm_firmware_load_name`, and the `nvkm_firmware_load()` selection macro.

## Control Flow

Drivers request a named or versioned firmware image, wrap it as an NVKM memory-like object, and later pass it to Falcon/GSP loaders or engine init code. The load macro first checks `Nv<name>Fw` to force a loader entry, then checks `Nv<name>FwVer`, iterates available loader versions, and stops on the first success or explicit requested version.

## State and Persistence Behavior

The wrapper owns image length, bytes, optional physical address, and DMA/SGT allocation state. Firmware contents remain immutable after construction and are released through the destructor or `nvkm_firmware_put`.

## Dependencies and Integration Points

It integrates Linux firmware loading with NVKM memory abstractions, `nvkm_blob`, driver config options, and subdevice logging. Falcon high-security firmware and GSP boot code consume this interface heavily.

## Risks

Option-driven loader selection can force unsupported versions; error pointers from the macro must be handled. DMA/SGT lifetime must outlive hardware transfer. Firmware path/version mismatches are runtime failures that normal build tests do not catch.

## Test Signals

Exercise missing firmware, forced firmware version options, RAM/DMA/SGT constructors, destructor cleanup under failure paths, and Falcon/GSP firmware boot on devices that require signed blobs.
