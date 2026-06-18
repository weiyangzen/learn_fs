<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_gbl.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_gbl.h

## Purpose

`qla_gbl.h` is the qla2xxx driver's global declaration hub. It collects cross-file function prototypes, global module parameters, exported data objects, interrupt handlers, mailbox helpers, IOCB builders, discovery helpers, target hooks, debugfs entry points, BSG handlers, flash/minidump support, NVMe hooks, EDIF hooks, and statistics APIs.

The file has no implementation logic, but it defines much of the driver's internal linkage contract.

## Important APIs, Types, And Data

- Initialization and adapter control prototypes cover PCI config, reset, diagnostics, ring setup, NVRAM config, firmware option updates, firmware load, loop resync, abort/quiesce, firmware dump allocation, and thermal reads.
- Discovery/session prototypes cover fabric login/logout, async login/logout/ADISC/PRLI/GNL/GPDB/GPSC/GFFID/GFPNID work, RSCN handling, fcport allocation/state, relogin, session deletion, and host map updates.
- IOCB and SCSI prototypes cover DSD/continuation building, SCSI start paths, DIF paths, markers, async SRB setup, IOCB allocation, SA replace issue, and SP release/timeout helpers.
- Mailbox and firmware service prototypes cover load/dump RAM, execute firmware, get/set options, port databases, link status, SFP reads/writes, trace enable/disable, flash update, remote registers, resource counts, and no-op mailboxes.
- Interrupt prototypes cover legacy and MSI-X handlers, response queue processing, SP lookup by handle, completed request processing, PUREX queueing, and PURLs handling.
- Support/debug/GS/attribute sections declare flash/NVRAM/optrom access, firmware dump routines, name-server commands, FDMI helpers, sysfs attributes, loopback/echo tests, and FCP priority config.
- EDIF declarations include SADB pool/release, SA delete pending checks, BSG app and ELS processing, doorbell/enode lifecycle, EDIF SCSI start, SA IOCB formatting/completion, auth ELS handling, and app-data cleanup.
- Global module parameters include logging, login retry, firmware loading, DIF, NVMe, queue, secure/EDIF, IOCB limit, and target options such as `ql2xsecenable` and `ql2xenforce_iocb_limit`.

## Control Flow

This header does not drive control flow directly. Instead, it enables qla source files to call each other across subsystem boundaries. For example, debugfs code calls mailbox and trace helpers declared here; EDIF code calls discovery, BSG, IOCB, target, and workqueue helpers; ISR code calls response and PUREX handlers; initialization code calls firmware, flash, and queue setup helpers. The organization by source file comments mirrors the driver's rough runtime phases: init, OS/workqueue, MID/NPIV, IOCB submission, mailbox services, interrupt handling, support/flash, debug, name server, attributes, debugfs, multi-queue, chip-family support, BSG, EDIF, NVMe, and stats.

## State And Persistence Behavior

The header declares state but does not own it. Extern module parameters persist for the module lifetime and influence behavior across initialization, discovery, I/O, and diagnostics. Extern caches such as `srb_cachep` and `qla_tgt_plogi_cachep` persist while the driver is loaded. Function prototypes manipulate persistent adapter, host, queue, port, firmware, flash, and EDIF state in their implementation files.

## Dependencies And Integration Points

The header includes `<linux/interrupt.h>` and depends on prior qla type definitions from `qla_def.h` and related headers. It is included broadly by qla2xxx implementation files, making it a central integration point. It also exposes interfaces to Linux SCSI, FC transport, BSG, NVMe FC, target mode, PCI error handling, debugfs, sysfs, mailbox, and firmware dump subsystems.

## Risks And Edge Cases

- Because this is a broad global header, adding prototypes here can mask poor subsystem boundaries and increase rebuild/review surface.
- Prototype drift between declarations and definitions will compile-fail, but semantic drift in ownership, locking, or completion expectations is harder to detect.
- Many functions operate on shared objects such as `scsi_qla_host_t`, `qla_hw_data`, `fc_port_t`, `srb_t`, request queues, and response queues. Callers must know locking and lifetime rules that are not encoded in prototypes.
- Duplicate or near-duplicate declarations exist for some functions, such as async abort and host attribute allocation, which increases maintenance noise.
- Module parameters declared here affect security and behavior globally, including EDIF enablement, firmware loading, NVMe enablement, queueing, logging, and reset behavior.

## Test Signals

The main validation signal is full-driver compile coverage across feature matrices and chip families. ABI-like internal tests should verify that every declared EDIF/debugfs/BSG/NVMe/target function has one definition and expected call sites. Runtime smoke tests should exercise initialization, discovery, SCSI I/O, mailbox, interrupt, debugfs, sysfs, BSG, target mode, NVMe, EDIF, firmware dump, flash access, and stats paths so declaration-level coupling is covered by real cross-file calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_gbl.h -->
