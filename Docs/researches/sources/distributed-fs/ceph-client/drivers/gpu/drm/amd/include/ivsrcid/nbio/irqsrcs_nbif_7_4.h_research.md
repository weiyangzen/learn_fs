# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/nbio/irqsrcs_nbif_7_4.h

## Purpose
This header defines NBIF 7.4/NBIO interrupt source IDs for chip error, doorbell, RAS, ATHUB error, PF/VF mailbox, slot/power, and PCIe atomic error events.

## Important APIs, Types, And Data
The constants include `CHIP_ERR_INT_EVENT`, `DOORBELL_INTERRUPT`, `RAS_CONTROLLER_INTERRUPT`, `ERREVENT_ATHUB_INTERRUPT`, PF-to-VF and VF-to-PF mailbox valid/ack IDs, `CHIP_DPA_INT_EVENT`, `CHIP_SLOT_POWER_CHG_INT_EVENT`, `ATOMIC_UR_OPCODE`, and `ATOMIC_REQESTEREN_LOW`. Values span `0x5E` through `0xCF`.

## Control Flow
There are no functions. NBIO implementations register selected IDs with `amdgpu_irq_add_id()` and RAS code uses the RAS/ATHUB error IDs to route NBIO-related interrupt events.

## State And Persistence
The constants are immutable. Runtime state is the NBIO/RAS/mailbox IRQ registration and any error counters or recovery state updated by handlers.

## Dependencies And Integration Points
The header is included by `nbif_v6_3_1.c`, `nbio_v4_3.c`, `nbio_v7_4.c`, `nbio_v7_9.c`, `amdgpu_ras.c`, and NBIO RAS manager code. It integrates with PCIe, doorbell handling during power states, SR-IOV PF/VF mailbox signaling, ATHUB error reporting, and RAS controller interrupts.

## Risks
PF/VF mailbox direction is encoded in separate source IDs; swapping valid and ack or PF-to-VF and VF-to-PF breaks virtualization communication. The macro `ATOMIC_REQESTEREN_LOW` preserves a spelling typo; renaming it without updating users would break builds. Wrong RAS IDs can hide fatal hardware error notifications.

## Test Signals
Build all NBIO users. Runtime validation should cover NBIO RAS interrupt registration, ATHUB error injection/reporting, SR-IOV PF/VF mailbox valid and ack flows, doorbell events around VDDGFX-off states, PCIe atomic error reporting, and slot power-change interrupt handling where supported.
