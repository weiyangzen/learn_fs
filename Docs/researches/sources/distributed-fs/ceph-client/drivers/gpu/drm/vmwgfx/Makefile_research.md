# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/Makefile

## Purpose

`vmwgfx/Makefile` defines the object list that composes the VMware virtual GPU DRM driver module and wires it to `CONFIG_DRM_VMWGFX`.

## Important APIs, Types, and Functions

- `vmwgfx-y`: ordered list of object files for execbuf, GMR/MOB memory, KMS, ioctls, resources, TTM buffers, command/fence/IRQ handling, overlay, contexts, surfaces, PRIME, command buffers, cotables, stream output, dirty tracking, GEM, VKMS integration, and cursor plane support.
- `obj-$(CONFIG_DRM_VMWGFX) := vmwgfx.o`: builds the aggregate object when the Kconfig symbol is enabled.

## Control Flow

Kbuild compiles each listed `*.o` and links them into `vmwgfx.o`. The final object is included in the kernel or module build depending on the tristate value.

## State and Persistence Behavior

There is no runtime state in the Makefile. The object list controls which driver subsystems are present in the binary.

## Dependencies and Integration Points

- Must stay aligned with source files and declarations used across vmwgfx.
- The device include headers in this research item support many objects listed here, especially command, execbuf, surface, context, MOB, cotable, and devcap code.

## Risks and Edge Cases

- Omitting an object can cause link failures or subtler missing feature paths if references are conditionally compiled.
- Adding new objects in the wrong aggregate or order can expose unresolved symbols during incremental builds.
- Generated or shared ABI headers are not listed here directly; they are pulled through includes and must remain in include paths.

## Test Signals

- `allyesconfig`, `allmodconfig`, and targeted `CONFIG_DRM_VMWGFX=m/y` builds catch object-list drift.
- Link tests should cover both module and built-in forms.
