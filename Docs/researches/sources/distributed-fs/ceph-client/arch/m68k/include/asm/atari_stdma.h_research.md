<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_stdma.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_stdma.h

## Purpose
This header declares the lock and ownership interface for Atari ST-DMA, a shared DMA engine used by multiple storage-related devices.

## Important APIs, Types, And Functions
- `stdma_try_lock()`, `stdma_lock()`, and `stdma_release()` manage exclusive access and associate an interrupt handler/data pair with the current owner.
- `stdma_islocked()` and `stdma_is_locked_by()` query ownership.
- `stdma_init()` initializes the ST-DMA arbitration layer.

## Control Flow
Device drivers acquire the ST-DMA lock before programming DMA registers, hold it while a transfer and handler are active, and release it when complete. Contenders either fail `try_lock` or block through `stdma_lock`.

## State And Persistence Behavior
Persistent state is implementation-owned: lock status, owner handler, owner data, and initialized hardware state. The header defines the external synchronization contract.

## Dependencies And Integration Points
It depends on `linux/interrupt.h` for `irq_handler_t` and integrates with Atari floppy, ACSI, SCSI, IDE, and other users of the shared ST-DMA hardware.

## Risks And Edge Cases
Releasing from the wrong owner or programming hardware without the lock can corrupt concurrent transfers. Interrupt handlers must match the owner or completion can be delivered to the wrong driver.

## Test Signals
Concurrent ST-DMA clients, failed try-lock paths, blocking lock/release ordering, owner checks, and DMA interrupt delivery for floppy/SCSI/IDE are direct signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_stdma.h -->
