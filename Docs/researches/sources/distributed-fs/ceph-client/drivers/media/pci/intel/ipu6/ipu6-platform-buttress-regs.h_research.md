# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-platform-buttress-regs.h

## Purpose
This header provides IPU6 buttress register offsets, bit definitions, power-state encodings, firmware-security IPC constants, interrupt masks, TSC controls, and default frequency-control values.

## Important APIs, Types, And Data
The file defines ISYS/PSYS frequency control registers and default ratios, power-state masks and FSM values, BTRS control bits, firmware reset/security registers, firmware source address registers, ISR status/enable/clear registers, CSE/ISH IPC doorbell/data/CSR definitions, fabric commands, TSC registers, and aggregate masks `BUTTRESS_IRQS` and `BUTTRESS_EVENT`.

## Control Flow
This is definition-only code. Consumers in buttress and PCI code use the constants to power domains, authenticate firmware, service IPC interrupts, configure arbitration, synchronize TSC, and react to fatal/non-fatal hardware events.

## State And Persistence
No runtime state is defined here. The macros describe memory-mapped hardware state in the IPU6 PCI BAR.

## Dependencies And Integration Points
It depends on Linux `BIT()` and `GENMASK()`. It is included by the PCI parent and ISYS files and supports integration with CSE/ISH firmware authentication and interrupt handling.

## Risks And Test Signals
Register definitions are hardware contracts. Wrong masks or offsets cause power/authentication/interrupt failures. Tests are hardware bring-up oriented: firmware auth, runtime PM transitions, ISR clearing, watchdog/fatal error reporting, TSC reads, and secure/non-secure boot.
