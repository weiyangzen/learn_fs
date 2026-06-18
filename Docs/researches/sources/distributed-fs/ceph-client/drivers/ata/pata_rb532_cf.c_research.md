# sources/distributed-fs/ceph-client/drivers/ata/pata_rb532_cf.c

## Purpose
Implements CompactFlash PATA support for MikroTik RouterBOARD 532 boards using platform resources and a GPIO/IRQ handshake.

## Important APIs, Types, And Functions
`struct rb532_cf_info` stores IRQ, GPIO descriptor, and mapped base. `rb532_pata_irq_handler()` acknowledges board-specific CF IRQ state before returning libata interrupt status. `rb532_pata_setup_ports()` fills ATA SFF register addresses at fixed RB500 offsets. `rb532_pata_driver_probe()` maps resources, requests GPIO/IRQ data, allocates the ATA host, and activates it. `rb532_pata_driver_remove()` detaches the host.

## Control Flow
Probe obtains memory resources and IRQ, maps the CF window, configures one SFF PIO port, records private info, and activates with a custom IRQ handler. The handler filters/acknowledges the hardware interrupt and then lets libata process the ATA interrupt.

## State And Persistence
Per-device state lives in `struct rb532_cf_info` and the mapped CF register window. Hardware IRQ/GPIO state persists across commands and is reset/acknowledged by the handler.

## Dependencies And Integration Points
Depends on platform bus, GPIO consumer API, RB532 board definitions, libata SFF PIO, and SCSI host registration.

## Risks And Edge Cases
The driver is board-specific and uses fixed register offsets. IRQ acknowledgement must match the board latch or interrupts can be lost or storm. It supports one port and PIO-only behavior.

## Test Signals
RouterBOARD 532 probe, register mapping, GPIO presence, IRQ delivery/ack, PIO identify/read/write, remove cleanup, and interrupt storm/lost-interrupt tests.
