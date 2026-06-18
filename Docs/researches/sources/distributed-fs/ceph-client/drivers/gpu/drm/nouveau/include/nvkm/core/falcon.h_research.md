# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/falcon.h

## Purpose

This header defines the core Falcon microcontroller service layer: IMEM/DMEM/EMEM transfer backends, Falcon reset/boot helpers, high-security firmware loading, and command/message queue management used by PMU, SEC2, GSP boot, video, and other firmware-backed engines.

## Important APIs, Types, and Functions

Important contracts include `enum nvkm_falcon_mem`, `struct nvkm_falcon_func_pio`, `struct nvkm_falcon_func_dma`, `struct nvkm_falcon_fw`, `struct nvfw_falcon_msg`, `nvkm_falcon_ctor`, `nvkm_falcon_reset`, `nvkm_falcon_pio_wr`, `nvkm_falcon_pio_rd`, `nvkm_falcon_dma_wr`, `nvkm_falcon_fw_ctor`, `nvkm_falcon_fw_oneinit`, `nvkm_falcon_fw_boot`, and the queue-manager APIs `nvkm_falcon_cmdq_send` and `nvkm_falcon_msgq_recv`.

## Control Flow

Callers construct a Falcon wrapper for a hardware engine, reset or select the unit, transfer firmware through PIO or DMA into IMEM/DMEM/EMEM, patch/sign high-security images when required, bind instance memory/VMM mappings, and then boot through mailbox handshakes. Queue users initialize firmware-advertised command and message rings, submit commands with callbacks and timeouts, and drain init or asynchronous messages.

## State and Persistence Behavior

The header describes persistent firmware image metadata, signature offsets, fuse/engine IDs, memory-window offsets, bootloader addresses, bound instance memory, VMM/VMA mappings, Falcon user ownership, and queue offsets. These fields are volatile driver state but they mirror persistent hardware microcode state until reset or teardown.

## Dependencies and Integration Points

It depends on `core/firmware.h`, `engine/falcon.h`, NVKM memory/VMM objects, subdev logging, and chip-specific implementations for GM200, GP102, TU102, GA100, and GA102. It is the bridge between generic firmware blobs and the engine-specific Falcon register programming.

## Risks

Incorrect IMEM/DMEM bounds, security flags, signature offsets, or mailbox success masks can leave firmware unbootable or silently boot the wrong image. Queue sequencing is timeout-sensitive and callback ownership must remain valid until replies arrive. RISC-V Falcon variants add reset and interrupt behavior that differs from classic Falcon units.

## Test Signals

Useful validation includes firmware load/boot on PMU/SEC2/GSP-backed engines, signature patch checks, secure and non-secure IMEM transfers, DMA-vs-PIO transfer fallback, timeout and mailbox failure injection, queue init-message receipt, and suspend/resume reset coverage.
