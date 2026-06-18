# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/disp.h

## Purpose

This header defines the display engine container, including head/IOR/output/connector lists, hotplug/vblank/user events, supervisor work, display channel objects, RAMHT/instance storage, and GSP-RM display integration.

## Important APIs, Types, and Functions

Important state is in `struct nvkm_disp`; event flags include `NVKM_DPYID_PLUG`, `NVKM_DPYID_UNPLUG`, `NVKM_DPYID_IRQ`, `NVKM_DISP_HEAD_EVENT_VBLANK`, and `NVKM_DISP_EVENT_CHAN_AWAKEN`. Constructors range from `nv04_disp_new` to `ga102_disp_new`.

## Control Flow

Generation-specific constructors populate the display engine, enumerate heads/outputs/connectors, create display channels, and wire hotplug/vblank events. GSP-capable paths use RM client/device/object handles and GSP events for HPD/IRQ delivery. Supervisor work coalesces pending display updates under its mutex.

## State and Persistence Behavior

The display object owns connector/output/head lists, event objects, assigned SOR masks, display instance/RAMHT objects, channel slots, masks/counts for display hardware blocks, and a client object protected by a spinlock. Hardware state persists in display channels and RM objects until engine fini.

## Dependencies and Integration Points

It connects NVKM display internals to DRM/KMS through higher Nouveau layers, GSP event handling, RAMHT legacy display objects, and per-generation display engine code.

## Risks

Incorrect masks or channel slot indexing can expose nonexistent hardware. Event loss affects hotplug/vblank correctness. GSP and non-GSP paths must keep object lifetime and assigned SOR accounting consistent.

## Test Signals

Validate connector enumeration, hotplug and unplug events, vblank delivery, supervisor work processing, display channel creation/destruction, GSP HPD/IRQ routing, and suspend/resume display reinitialization.
