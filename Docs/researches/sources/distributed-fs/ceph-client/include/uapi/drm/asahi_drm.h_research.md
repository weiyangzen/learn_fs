# sources/distributed-fs/ceph-client/include/uapi/drm/asahi_drm.h

## Purpose
Defines the Asahi Apple GPU DRM UAPI for parameter discovery, GPU VM management, GEM allocation and binding, queue creation, sync objects, command submission, timestamps, render and compute command payloads.

## Important APIs, Types, And Functions
Exports ioctl IDs and `DRM_IOCTL_ASAHI_*`, global parameter struct, feature bits, VM create/destroy/bind, GEM create/mmap/bind-object, command types, priorities, queue create/destroy, sync item structs, submit command-buffer format, attachment hints, render flags, ZLS buffers, timestamp objects, helper/background/end-of-tile program descriptors, render/compute command structs, and GPU time query.

## Control Flow
The ABI defines an explicit userspace flow: query parameters, create VM with kernel VA reservation, create and bind GEM objects, optionally bind special timestamp objects, create a queue, submit a flat command buffer containing headers and typed payloads with barriers and sync arrays, then destroy queues/VMs.

## State, Persistence, And Dependencies
Persistent kernel state includes GPU VMs, GEM BOs, special bound objects, queues, sync dependencies, and submitted firmware jobs. Command payloads describe transient render/compute state and firmware-visible control register values. It depends on `drm.h`.

## Integration Points
Used by Asahi Mesa drivers, Asahi DRM kernel driver, DRM syncobj, GEM/dma-buf, firmware scheduling, and virtgpu-friendly command transport because submit buffers avoid CPU pointers.

## Risks
The header documents strict extensibility rules: 64-bit alignment, zeroed padding, append-only ioctl IDs, flag preservation, size-tagged indirect objects, and driver-version updates for new fields. Violating these breaks old userspace or old kernels. VM ranges, barriers, and command sizes need strong validation.

## Test Signals
UAPI struct size/offset tests, zero-padding rejection tests, old/new struct size compatibility, VM range validation, GEM bind/unbind tests, queue lifecycle, command-buffer parser tests, barrier ordering tests, syncobj timeline tests, render/compute conformance, and timestamp frequency checks.
