# sources/distributed-fs/ceph-client/include/linux/mmc/sdio.h

## Purpose
`mmc/sdio.h` defines SDIO protocol constants: SDIO command opcodes, CMD52/CMD53 argument layouts, R4/R5 response bits, Card Common Control Register addresses and bits, and Function Basic Register addresses and bits.

## Important APIs, Types, And Functions
Important constants include `SD_IO_SEND_OP_COND`, `SD_IO_RW_DIRECT`, `SD_IO_RW_EXTENDED`, R4 voltage/memory bits, R5 error and state macros, CCCR revisions, SD physical revisions, IO enable/ready/interrupt registers, bus interface bits, capabilities bits, CIS pointer, suspend/select/exec/ready registers, block size, power control, high-speed/UHS/drive strength/interrupt extension registers, and FBR base, interface, power, CIS, CSA, and block-size registers.

## Control Flow And State
There is no active code. The SDIO core uses these constants to enumerate function 0 and functions 1-7, enable functions, set block sizes, route interrupts, choose bus width and speed, parse CIS/FBR data, and issue byte or extended transfers. CMD52 handles direct register access; CMD53 handles byte or block data transfers with fixed or incrementing address semantics.

## Dependencies And Integration Points
The file is standalone and integrates with `sdio_func.h` I/O APIs, `card.h` SDIO CCCR/CIS state, host SDIO IRQ callbacks, SDIO function drivers, and MMC command submission from `core.h`.

## Risks And Test Signals
Risks include bad CMD52/CMD53 argument encoding, incorrect R5 error handling, CCCR/FBR revision drift, enabling interrupts or high-speed mode on unsupported cards, and mishandled low-speed 4-bit constraints. Test signals include SDIO enumeration, function enable/disable, block-size negotiation, byte and block I/O, IRQ claim/release, high-speed/UHS switching, and CIS/FBR parsing tests.
