# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/ivsrcid_vislands30.h

## Purpose
This legacy Volcanic Islands interrupt-vector source ID header defines display, graphics, memory, media, SDMA, thermal, SMU, BIF, and virtual-memory source IDs plus extended IDs. It is shared by older AMDGPU display, GFX, GMC, UVD, VCE, SDMA, and PowerPlay paths.

## Important APIs, Types, And Data
Display IDs cover D1-D6 vupdate, graphics page flip, vertical interrupts, external timing sync events, HPD A-F, and HPD RX A-F. System and memory IDs include SRBM read timeout/context switch/register access errors, system/SEM/GFX page-invalid and memory-protection faults, and synthetic `VM_CONTEXT_ALL` IDs. Media IDs include UVD encoder/general/system messages and VCE trap with extended IDs for general-purpose, low-latency, and real-time queues.

GFX/CP IDs cover ring/IB interrupts, PM4 errors, EOP, bad opcode, privileged faults, wait-mem-semaphore fault, GUI idle/busy, compute query status, wait-reg-mem timeout, semaphore incomplete, preempt ack, GPF, GDS allocation, ECC, RLC streaming performance monitor, GRBM timeout/idle, and SQ interrupt. SDMA IDs cover atomic, ECC, trap, semaphore, preempt, VM hole, context empty, invalid doorbell, frozen, poll timeout, and SRBM write. Thermal/SMU IDs include TSS low/high transitions, thermal trigger, display timer triggers, GPIO 19, and BIF PF/VF mailbox events. `VISLANDS30_IV_EXTID_NONE` and `VISLANDS30_IV_EXTID_INVALID` define extended-ID sentinels.

## Control Flow
There is no code. Legacy and DCE display paths register these IDs with `amdgpu_irq_add_id()` and decode source/extended IDs in IRQ service implementations. Older GFX/GMC/UVD/VCE/SDMA/PowerPlay code uses the same constants for fault, media, and thermal interrupt registration.

## State And Persistence
The constants are immutable legacy hardware ABI. Runtime state is the IRQ registration, enabled masks, and handler dispatch based on source and extended IDs.

## Dependencies And Integration Points
Integration spans `dce_v10_0.c`, `amdgpu_dm.c`, DCE IRQ services, `gfx_v8_0.c`, `gmc_v7_0.c`, `gmc_v8_0.c`, UVD/VCE implementations, SDMA v2/v3, SMU7 hardware manager, SMU helper, and VKMS compatibility code.

## Risks
Several events share a source ID and are distinguished by extended ID, especially vertical interrupt groups and HPD/HPD RX. The file also defines synthetic IDs that are not direct hardware source IDs. Treating all constants as raw hardware values or ignoring ext IDs can misroute display or VM fault events. Because this header is used by many older code paths, even small value changes have broad regression risk.

## Test Signals
Build legacy DCE, GFX8, GMC7/8, UVD, VCE, SDMA v2/v3, and SMU7 paths. Runtime checks include HPD and page flip/vblank delivery, VM fault interrupts, CP EOP/fault handling, UVD/VCE interrupts, SDMA trap/SRBM write interrupts, thermal events, and PF/VF mailbox interrupts where virtualization is enabled.
