<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_psc.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_psc.h

## Purpose
`mac_psc.h` defines the Apple Peripheral System Controller used on AV Macs for DMA, sound, SCC, Ethernet, SCSI, FDC, and interrupt control.

## Important APIs, Types, and Functions
It defines `PSC_BASE`, IFR/IER offsets, one-shot DMA control/address/length/command offsets for SCSI, Ethernet, FDC, SCC receive/transmit channels, sound DMA/control/source/status registers, global `psc`, interrupt registration/enable/disable APIs, and inline byte/word/long accessors.

## Control Flow, State, and Persistence
The inline accessors directly read/write the mapped PSC register space. PSC DMA state persists in hardware channel registers; sound DMA may run continuously.

## Dependencies and Integration Points
Mac AV Ethernet, SCSI, serial, floppy, sound, and interrupt code use these offsets. PSC interrupts occupy several level groups in `macints.h`.

## Risks
Some fields are explicitly inferred or unknown. Sound DMA can overwrite memory if not disabled early. DMA channels use paired one-shot buffers, so driver sequencing must flip channels correctly.

## Test Signals
Signals include PSC interrupt enable/disable per level, MACE Ethernet DMA, SCSI/FDC/SCC DMA transfers, sound DMA shutdown at boot, and correct byte/word/long register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_psc.h -->
