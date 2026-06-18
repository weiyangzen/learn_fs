# sources/distributed-fs/ceph-client/include/uapi/linux/kfd_sysfs.h

## Purpose
`kfd_sysfs.h` defines bit masks and numeric values exported through AMD KFD sysfs topology nodes for HSA node capabilities, debug capabilities, memory heaps, caches, and IO links.

## Important APIs, Types, and Functions
Capability bits describe hotplug, ATS, graphics sharing, queue size constraints, idle events, VA limits, watchpoints, doorbell types, trap-debug support, memory RAS/EDC, SVM API, coherent host access, firmware trap support, precise ALU/memory debug support, and per-queue reset support. `HSA_CAP2_*` extends capabilities. Debug properties define watch address mask fields and dispatch-info validity. Memory heap types, memory flags, cache types, IO link types, and IO link flags describe topology resources and link semantics.

## Control Flow
Userspace reads sysfs topology attributes, decodes numeric bitfields using these constants, and decides which ROCm/HSA features can be enabled for each GPU node and link.

## State and Persistence
The values reflect live hardware/driver topology and capabilities. They persist while the device is present but can change with driver updates, hotplug, or reset.

## Dependencies and Integration Points
The header has no includes. Integration points include `/sys/class/kfd/kfd/topology`, ROCm runtime discovery, debuggers, memory allocators, peer-to-peer routing, and capability checks before using `kfd_ioctl.h` ioctls.

## Risks and Test Signals
Tests should verify bit decoding, reserved-mask handling, consistency with ioctl-reported capabilities, multi-GPU IO link types/flags, and capability-gated feature enablement. ABI risk is in preserving bit meanings and not reusing reserved bits incorrectly.
