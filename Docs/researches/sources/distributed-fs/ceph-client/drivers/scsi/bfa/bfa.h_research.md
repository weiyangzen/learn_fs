# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa.h

## Purpose
`bfa.h` is the central HAL-facing public header for the QLogic/Brocade BR-series Fibre Channel adapter layer. It connects the driver-facing `bfad` code, common-service helpers, BFI firmware messaging, IOC management, and service definitions into one control plane for queue management, interrupts, IOCFC lifecycle, completion callbacks, and adapter query helpers.

## Important APIs, Types, and Macros
The key type is `struct bfa_iocfc_s`, which owns the IOCFC state machine pointer, firmware/driver configuration, request/response circular queue indices, queue DMA descriptors, shadow producer/consumer DMA areas, firmware configuration request/response pages, device register pointers, chip-specific `struct bfa_hwif_s`, callback queue entries, Fabric Assigned Address query state, and IOCFC memory descriptors. Queue macros such as `bfa_reqq_next`, `bfa_reqq_produce`, `bfa_reqq_full`, `bfa_rspq_pi`, `bfa_rspq_ci`, and `bfa_rspq_elem` define the ABI between host ring state and firmware queue registers. Callback helpers `bfa_cb_queue`, `bfa_cb_queue_once`, `bfa_cb_queue_status`, and pending queue initializers standardize deferred callback dispatch. Public lifecycle APIs include `bfa_cfg_get_default`, `bfa_cfg_get_meminfo`, `bfa_attach`, `bfa_detach`, `bfa_iocfc_init`, `bfa_iocfc_start`, `bfa_iocfc_stop`, `bfa_iocfc_enable`, `bfa_iocfc_disable`, and interrupt APIs `bfa_intx`, `bfa_isr_enable`, `bfa_isr_disable`, `bfa_msix_*`.

## Control Flow and State
This header declares the IOCFC event enum used by `bfa_core.c`: init/start/stop/enable/disable requests, IOC enabled/disabled/failure callbacks, dynamic configuration completion, and firmware config completion. The queue macros are control-flow critical because most modules reserve a firmware message with `bfa_reqq_next`, fill it, then publish it with `bfa_reqq_produce`, which stamps the hardware queue id and writes the new producer index to the mapped register.

## State and Persistence Behavior
State is in memory and hardware-facing DMA, not filesystem persistence. Persistent adapter settings enter via firmware/config flash responses and are exposed through `cfgrsp`, LUN mask accessors, boot WWN helpers, and adapter/IOC macros. Ring indices and shadow pointers are volatile coordination state shared with firmware and must preserve power-of-two queue sizing assumptions.

## Dependencies and Integration Points
It depends on `bfad_drv.h` for Linux driver primitives, `bfa_cs.h` for tracing/state-machine/list helpers, `bfa_defs_svc.h` for IOCFC service structs, `bfi.h` for firmware message layouts, and `bfa_ioc.h` for IOC services. Hardware callback declarations split CB, CT, and CT2 ASIC behavior behind `bfa_hwif_s`.

## Risks and Test Signals
High-risk areas are ring wrap math, DMA pointer alignment, endian conversion, callback queue lifetime, and missing hardware callback installation. Test signals include queue full/resume behavior under load, MSI-X and INTx interrupt paths, IOC init/disable/re-enable cycles, failed firmware config replies, min-config LUN mask returns, and all ASIC id branches for CB, CT, and CT2.
