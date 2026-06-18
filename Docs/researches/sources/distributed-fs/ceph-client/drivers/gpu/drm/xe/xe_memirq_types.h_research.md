# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_memirq_types.h

## Purpose
`xe_memirq_types.h` defines the memory IRQ page-layout offsets and the runtime storage object for memory-based interrupts.

## Important APIs, Types, And Functions
- `XE_MEMIRQ_STATUS_OFFSET(inst)` defines status report page offset.
- `XE_MEMIRQ_SOURCE_OFFSET(inst)` defines source report page offset.
- `XE_MEMIRQ_ENABLE_OFFSET` defines interrupt mask offset.
- `struct xe_memirq` stores the BO, source/status/mask iosys maps, and enabled flag.

## Control Flow
The implementation uses the offsets to allocate and index page-like regions inside a single BO. LRC/GuC programming consumes the derived GGTT addresses.

## State And Persistence
The struct persists per tile. Hardware and software share the BO contents; software owns the `enabled` flag and map metadata.

## Dependencies And Integration Points
Depends on `iosys-map` and forward-declares `struct xe_bo`. Used by tile state, IRQ code, memirq implementation, and LRC context setup.

## Risks
Offsets are ABI-like hardware contract values. Changing them without matching hardware programming would break interrupt delivery. The enabled flag is separate from hardware mask contents, so both must remain synchronized.

## Test Signals
Static layout assertions, pointer calculation tests, and dispatch tests validating source/status/mask offsets.
