# sources/distributed-fs/ceph-client/lib/devmem_is_allowed.c

## Purpose
Provides the generic fallback policy for `/dev/mem` physical-memory access when an architecture does not provide a stricter implementation.

## APIs, Types, and Functions
Defines `int devmem_is_allowed(unsigned long pfn)`, returning `1` unconditionally.

## Control Flow
There is no branching: every page frame number is allowed by this generic helper.

## State and Persistence
No state is read or modified.

## Dependencies and Integration Points
This weak/default-style library implementation is used by `/dev/mem` access checks on architectures that do not override it. It integrates with memory device drivers and security policy controlled by architecture and Kconfig choices.

## Risks and Test Signals
The risk is permissive raw physical memory access if used on platforms that should restrict RAM or device regions. Test signals include architecture build coverage ensuring stricter implementations override this where required, `/dev/mem` access tests under `CONFIG_STRICT_DEVMEM`, and security policy review for target architectures.
