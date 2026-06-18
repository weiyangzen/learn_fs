<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/falcon.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/falcon.c

## Purpose

`falcon.c` implements the shared engine wrapper for NVIDIA Falcon microcontroller-based engines. It handles class enumeration, engine context object binding, interrupt handling, firmware discovery/loading, IMEM/DMEM upload, boot, shutdown, and construction.

## Important APIs, Types, And Functions

`nvkm_falcon_oclass_get()` enumerates engine-specific supported classes. `nvkm_falcon_cclass_bind()` allocates a 256-byte context object. `nvkm_falcon_intr()` decodes Falcon interrupt status, looks up the current channel by instance address, dispatches engine-specific interrupts, logs halted microcode, and acks bits. `nvkm_falcon_oneinit()` detects Falcon version, secret level, and code/data limits. `nvkm_falcon_init()` waits for secure halt where needed, loads internal or external firmware, allocates core memory for self-bootstrapping firmware, uploads code/data through old or new Falcon register interfaces, zeros remaining DMEM, starts execution, and calls an optional engine init hook. `nvkm_falcon_fini()` disables FIFO/CHSW and frees poweroff-only resources. `nvkm_falcon_new_()` constructs the engine.

## Control Flow

Engine-specific code calls `nvkm_falcon_new_()` with firmware blobs or empty firmware pointers. Oneinit records hardware caps. Init first handles secure/halt state, disables interrupts, tries a self-bootstrapping firmware file, then split data/code firmware files, copies firmware into memory or Falcon IMEM/DMEM, starts execution, and enables FIFO/CHSW. Interrupts map Falcon instance state back to a FIFO channel and delegate engine-specific work before acking.

## State And Persistence Behavior

`struct nvkm_falcon` persists function pointers, MMIO base, version/secret/cap limits, code/data buffers, external-firmware ownership, and optional core memory. External firmware vmalloc buffers are freed on poweroff. Core memory is also released on poweroff.

## Dependencies And Integration Points

It depends on generic engine construction, firmware loader, GPU object/memory helpers, MC enable checks, timer polling, FIFO channel lookup, and engine-specific Falcon function tables.

## Risks And Edge Cases

Firmware loading has multiple fallback names and can fail with `-ENODEV`. Code/data sizes are checked against hardware limits only for direct upload. External self-bootstrapping images are copied to instance memory and programmed through bootstrap registers. Interrupt handling must tolerate no channel lookup. Poweroff cleanup must only free externally owned buffers.

## Test Signals

Signals include firmware load logs identifying self-bootstrapping or split images, Falcon version/limit debug output, no `ucode exceeds falcon limits` errors, handled engine-specific interrupts, clean halted microcode acks, and successful suspend/resume or poweroff reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/falcon.c -->
