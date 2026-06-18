<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/internals.h -->
# sources/distributed-fs/ceph-client/drivers/nvmem/internals.h

## Purpose
Defines the private `struct nvmem_device` layout and internal layout-bus hooks shared between the NVMEM core and layout implementation.

## Important APIs, Types, And Functions
`struct nvmem_device` stores owner, driver-core device, stride, word size, id, refcount, size, access flags, type, compatibility sysfs attributes, cell list, DT fixup callback, keepout metadata, provider callbacks, write-protect GPIO, active layout, provider private pointer, and sysfs-cell population state. Internal declarations cover layout bus register/unregister, layout populate, and layout destroy, with OF-disabled stubs.

## Control Flow
The header has no runtime flow. It is included by `core.c` and `layouts.c`; when OF is disabled, layout operations compile to no-ops.

## State And Persistence
Defines in-memory framework state only. Persistence belongs to providers.

## Dependencies And Integration Points
Depends on device model, NVMEM public consumer/provider headers, GPIO descriptors through the core, and OF conditional compilation.

## Risks
Changing this private structure affects core/layout assumptions and lifetime management. The OF stubs must match real function signatures so non-OF builds remain valid.

## Test Signals
Build with and without `CONFIG_OF`, with sysfs enabled and disabled, and run provider registration plus layout population tests to catch structure or stub mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/internals.h -->
