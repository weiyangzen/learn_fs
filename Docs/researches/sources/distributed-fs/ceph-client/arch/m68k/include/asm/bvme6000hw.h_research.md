<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bvme6000hw.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/bvme6000hw.h

## Purpose
This header maps BVME6000 board hardware: PIT, RTC, Ethernet, SCSI, SCC serial, configuration switches, IRQ assignments, and VME address control registers.

## Important APIs, Types, And Functions
- `PitRegsPtr` and `RtcPtr_t` map PIT and RTC register blocks.
- Fixed addresses define PIT, RTC, Intel i596 Ethernet, local IRQ/status, NCR53C710 SCSI, SCC channels, config register, and VME ACR registers.
- IRQ constants map printer, timer, Ethernet, SCSI, RTC, abort, and SCC subinterrupts to Linux IRQ numbers.
- `bvme_acr_*` macros expose VME address control registers as volatile bytes.

## Control Flow
Board setup and drivers directly program the mapped registers. Interrupt code uses the IRQ constants to register handlers and read status. VME setup writes ACR registers to configure bus address translation.

## State And Persistence Behavior
State resides in board hardware registers and switch inputs. The header itself has no state but provides direct mutable lvalues for VME address control.

## Dependencies And Integration Points
It depends on `asm/irq.h` and integrates with BVME6000 platform setup, timer, RTC, Ethernet, SCSI, serial, abort button, and VME bus code.

## Risks And Edge Cases
Fixed physical addresses and byte-wide ACR access must match board wiring. Incorrect IRQ numbering can misroute SCC subinterrupts. VME address control writes can make bus devices inaccessible.

## Test Signals
BVME6000 boot, PIT timer tick, RTC access, Ethernet and SCSI interrupts, SCC channel TX/RX, abort interrupt, config switch reading, and VME device probing validate this map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bvme6000hw.h -->
