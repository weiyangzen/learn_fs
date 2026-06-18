# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfi.h

## Purpose
`bfi.h` defines the low-level Brocade/QLogic firmware interface ABI shared by BFA modules: common message headers, DMA address/SG formats, message classes, IOC control and attributes, preboot configuration, message queues, generic port messages, ASIC block control, CEE/SFP/flash/diagnostic/PHY/FRU message layouts.

## Important APIs, Types, and Functions
The file is packed with `#pragma pack(1)`. Core definitions include `struct bfi_mhdr_s`, `bfi_h2i_set`, `bfi_i2h_set`, `BFA_I2HM`, `union bfi_addr_u`, `struct bfi_sge_s`, `struct bfi_alen_s`, `struct bfi_sgpg_s`, `struct bfi_msg_s`, and `struct bfi_mbmsg_s`. `enum bfi_mclass` assigns firmware message classes for IOC, diagnostics, flash, CEE, FCPORT, IOCFC, ABLK, UF, FCXP, LPS, RPORT, ITN, IOIM, TSKIM, port, SFP, PHY, and FRU. IOC types define adapter attributes, firmware image headers, boot controls, heartbeat, state machine values, and mailbox unions. Later sections define preboot config, message queue rings and doorbells, port stats commands, adapter-block PF/optrom commands, CEE/SFP/flash operations, diagnostic tests including D-port notifications, external PHY operations, and FRU read/write messages.

## Control Flow
This header has no runtime control flow, but BFA modules populate H2I structures, post them to mailbox/message queues, and decode I2H responses using these layouts. Macros set headers and compute DMA segment counts/offsets. Queue macros update producer/consumer indices and calculate free entries.

## State and Persistence
It describes firmware-visible state rather than driver-owned state. Persistent domains include flash image and partitions, boot/preboot configuration, adapter properties, SFP/PHY/FRU data, and firmware image metadata. Runtime domains include IOC heartbeat/state, message queue indices, stats DMA buffers, trace offsets, and diagnostic results.

## Dependencies and Integration Points
The file includes `bfa_defs.h` and `bfa_defs_svc.h` for shared types. Higher-level BFA code and BFAD BSG/debugfs commands rely on these constants and packed structures when communicating with firmware and reading BAR/flash/debug regions.

## Risks
This is a hardware/firmware ABI. Packing, endian fields, bitfields, opcode values, sizes, and queue arithmetic must remain exact. Several macros assume power-of-two queue depths or particular segment sizes. Bitfield layout in `struct bfi_sge_s` varies by endian and must match firmware. Any structure drift can cause firmware misinterpretation.

## Test Signals
Validation should include build-time structure-size/offset assertions where available, endian tests, firmware handshake tests for IOC enable/getattr/heartbeat, message queue wraparound/free-count tests, flash/diag/PHY/FRU command round trips, and compatibility checks across ASIC generations.
