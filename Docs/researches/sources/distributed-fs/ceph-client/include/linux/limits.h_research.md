# sources/distributed-fs/ceph-client/include/linux/limits.h

Purpose: extends UAPI/vDSO limits with kernel typed maximum and minimum constants.

Important APIs and types: defines `SIZE_MAX`, `SSIZE_MAX`, `PHYS_ADDR_MAX`, `RESOURCE_SIZE_MAX`, and signed/unsigned 8/16/32/64-bit min/max constants.

Control flow: included by kernel code needing type bounds for validation, allocation, arithmetic, or ABI clamping.

State and persistence: no state is stored.

Dependencies and integration points: depends on UAPI limits, kernel integer types, and vDSO limits. It is widely included by generic kernel code.

Risks and test signals: risks are type-cast mistakes, duplicate macro conflicts, and word-size assumptions. Test compile coverage on 32/64-bit architectures and boundary checks in consumers.
