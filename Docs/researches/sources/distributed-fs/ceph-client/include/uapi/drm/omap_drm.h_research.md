# sources/distributed-fs/ceph-client/include/uapi/drm/omap_drm.h

## Purpose

`omap_drm.h` defines the TI OMAP DRM UAPI for chipset parameters and GEM BO allocation/info, including scanout, CPU cacheability, and TILER-backed tiled buffers. The complete 126-line header was read.

## Important APIs, Types, and Functions

Public ioctls are `GET_PARAM`, `SET_PARAM`, `GEM_NEW`, deprecated `GEM_CPU_PREP`, deprecated `GEM_CPU_FINI`, and `GEM_INFO`. Important types are `drm_omap_param`, `union omap_gem_size`, `drm_omap_gem_new`, `omap_gem_op`, CPU prep/fini structs, and `drm_omap_gem_info`. Flags cover scanout, cached/WC/uncached mapping, and TILER 8/16/32 modes.

## Control Flow

Userspace queries or sets parameters, creates a GEM object using byte size for linear buffers or width/height for tiled buffers, queries mmap offset and virtual mmap size with `GEM_INFO`, and may call deprecated CPU prep/fini around software access.

## State and Persistence Behavior

GEM handles persist under DRM lifetime. Tiled buffers expose a virtual mmap size that can differ from physical backing. CPU prep/fini represent cache synchronization around access rather than durable object state.

## Dependencies and Integration Points

Depends on `drm.h`. Integrates with OMAP DRM, DSS scanout, TILER layout, GEM mmap/open infrastructure, and older userspace using deprecated CPU sync ioctls.

## Risks and Edge Cases

Primary risks are interpreting `union omap_gem_size` correctly, validating cache/TILER flag combinations, preserving deprecated ioctl compatibility, and ensuring CPU fini cache ops cover the whole buffer despite placeholder region fields.

## Test Signals

Cover chipset parameter query, linear and tiled GEM_NEW, scanout/cache combinations, `GEM_INFO` mmap offset and virtual size, invalid flag/padding rejection, and deprecated CPU prep/fini compatibility.
