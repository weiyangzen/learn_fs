# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_device.h

## Purpose

`radeon_device.h` is a very small private header for the Radeon device layer. In this snapshot it only exposes the virtualization probe helper needed outside `radeon_device.c`, while preserving the long-standing private-header include guard and license block.

## Important APIs, Types, and Functions

- `bool radeon_device_is_virtual(void);` reports whether the driver appears to run under a hypervisor. The implementation is architecture-dependent: on x86 it checks `X86_FEATURE_HYPERVISOR`; on non-x86 it returns false.

## Control Flow

The header contributes no control flow by itself. Consumers include it when they need the virtualization query without depending on the full `radeon.h` implementation details. `radeon_drv.c` includes it as part of driver entry setup, and `radeon_device.c` provides the implementation used during boot/post checks and virtualized ASIC handling.

## State and Persistence Behavior

There is no persistent state in the header. The exported function reads CPU/platform capability state at runtime and does not cache results here.

## Dependencies and Integration Points

The file integrates the device lifecycle code with other Radeon components through a single declaration. Its guard name, `__RADEON_DEVICE_H__`, prevents repeated inclusion. The actual implementation depends on kernel CPU feature helpers when built on x86.

## Risks and Edge Cases

- The API is intentionally coarse: non-x86 platforms always report false in the current implementation even if a hypervisor is present.
- Because the header is private and minimal, adding more declarations should be weighed against using `radeon.h` or a more focused subsystem header.

## Test Signals

Build coverage should ensure every include compiles without requiring hidden transitive headers. Runtime coverage should check pass-through behavior that uses `radeon_device_is_virtual()` to force ASIC init for newer families.
