# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx.h

## Purpose
`aic79xx.h` is the core OS-neutral definition header for Adaptec AIC79xx Ultra320 SCSI controllers. It defines register-facing macros, chip/features/bugs/flags enums, hardware and software SCB layouts, queue and target-mode structures, transfer negotiation state, SEEPROM/VPD formats, flexport constants, the main `ahd_softc`, and public function declarations used by the aic79xx core and OS modules.

## Important APIs, Types, And Functions
Important constants include target/lun limits, max transfer size, SCB queue sizes, target-mode command counts, and bus reset delay. Major structures include `struct hardware_scb`, `struct ahd_dma_seg`, `struct ahd_dma64_seg`, `struct scb`, `struct scb_data`, `struct target_cmd`, `struct ahd_tmode_tstate`, `struct ahd_transinfo`, `struct seeprom_config`, `struct vpd_config`, `struct ahd_suspend_state`, `struct ahd_completion`, `struct ahd_softc`, `struct ahd_devinfo`, and `struct ahd_pci_identity`. The header declares public core APIs for PCI config, SCB management, initialization, reset, flexport access, error recovery, device info compilation, negotiation updates, target mode, and debug dumping.

## Control Flow
As a header, it defines no direct execution path. Its declarations shape the aic79xx core control flow: allocate/init `ahd_softc`, configure PCI or other bus front end, allocate SCBs and DMA maps, queue SCBs through QINFIFO, complete through QOUTFIFO, manage pending/disconnected queues, negotiate SPI width/sync/PPR settings, apply hardware bug workarounds, handle target-mode events, and suspend/resume register state.

## State And Persistence Behavior
`struct ahd_softc` is the central persistent runtime state for a controller. It holds bus handles, SCB data, pending SCBs, register mode state, platform data, target-mode state, timer/statistics fields, chip/features/bugs/flags, SEEPROM config, QIN/QOUT FIFO cursors, qfreeze count, critical sections, overrun buffer, channel and ID information, target command FIFO, message buffers, DMA shared data maps, suspend snapshots, interrupt coalescing parameters, and user negotiation bitmasks.

## Dependencies And Integration Points
The header includes generated `aic79xx_reg.h`, so it depends on the Makefile/aicasm generation path. It also depends on platform typedefs supplied by OS-specific headers before inclusion, such as bus-space, DMA, device, and queue/list types. It is consumed by aic79xx core, PCI front end, OSM layer, proc/debug code, and generated register pretty printers.

## Risks
This header is a dense hardware ABI. Layout changes in `struct hardware_scb`, SG entries, completion entries, or SEEPROM/VPD structs can break firmware communication. Many flags represent silicon errata; failing to set the right bug bits can cause subtle data corruption or failed recovery. Queue constants assume power-of-two FIFO sizes and tag ranges. The generated register dependency means stale `aic79xx_reg.h` can desynchronize macros from sequencer firmware.

## Test Signals
Signals include successful builds with generated register headers, SCB allocation and tag-index mapping up to queue limits, correct 32-bit and 64-bit SG programming, negotiation transitions for async, sync, DT, packetized, and paced modes, reset and qfreeze behavior, suspend/resume state restoration, SEEPROM checksum and parse behavior, and debug dumps that decode register state consistently with generated tables.
