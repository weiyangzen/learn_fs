# sources/distributed-fs/ceph-client/drivers/scsi/isci/phy.h

## Purpose

`phy.h` declares the `isci` phy object, phy-specific hardware frame/property structures, phy counter IDs, phy state IDs, and exported phy operations. It is the shared contract between host, port, completion, and libsas phy-control code.

## Important APIs, Types, and Functions

`struct isci_phy` contains the SCI state machine, owning port pointer, negotiated link rate, attached protocol, phy index, deferred broadcast flag, link-training flag, SATA timer, transport and link-layer MMIO register pointers, embedded `asd_sas_phy`, SAS address, and a union for the last received SAS identify frame or SATA device-to-host FIS.

`struct sci_phy_cap` models link-layer PHY capabilities with start, SSC, generation support, requested link rate, and parity bits. `struct sci_phy_proto` models SAS/STP/SMP/SSP initiator and target protocol bits. `struct sci_phy_properties`, `struct sci_sas_phy_properties`, and `struct sci_sata_phy_properties` describe runtime properties for generic, SAS, and SATA phys. `enum sci_phy_counter_id` lists optional counter IDs for frames, dwords, sync loss, disparity, CRC, timeout primitives, credit blocking, short frames, exhausted credit, after-DONE frames, and speed-negotiation sync errors.

`enum sci_phy_states` defines the base and starting-substate machine: initial, stopped, starting, await OSSP, await SAS speed, await IAF, await SAS power, await SATA power, await SATA phy, await SATA speed, await signature FIS, final, ready, resetting, and final. Exported functions cover construction, port assignment, initialization, start/stop/reset/resume, transport setup, event/frame handling, power consumption, address/protocol getters, link-rate getter, libsas initialization, and libsas phy control.

## Control Flow

The header-level state model is implemented in `phy.c`. Host initialization constructs each phy on the dummy port, initializes register windows, and transitions to stopped. Controller start invokes `sci_phy_start()`, event completions call `sci_phy_event_handler()`, unsolicited frames call `sci_phy_frame_handler()`, and final link-training success enters ready and notifies the controller. Port code can reassign phys with `sci_phy_set_port()`, and libsas management calls `isci_phy_control()`.

## State and Persistence Behavior

All state is in memory and hardware registers. The SAS address is copied from OEM parameters during `isci_phy_init()` and exposed through the embedded libsas phy. The received-frame union is the last link-discovery frame state used by libsas and device discovery; it is not persisted.

## Dependencies and Integration Points

The header includes SAS/libsas definitions, common `isci.h`, and `sas.h`, and forward-declares `struct isci_host`. It depends on register type declarations from included driver headers through users of the function prototypes. Integration points include host startup, port configuration, unsolicited-frame control, libsas phy management, and ATA signature FIS handling.

## Risks and Edge Cases

The `PHY_STATES` macro is used both for string names and enum values; edits must keep ordering stable with the state table in `phy.c`. `to_iphy()` relies on `asd_sas_phy` being embedded in `struct isci_phy`. The received-frame union overlays SAS and SATA frame formats, so consumers must check protocol/state before interpreting it. Timer, port, and register pointers are initialized in different phases, so callers must not invoke runtime handlers before `sci_phy_initialize()`.

## Test Signals

Compile signals include state enum/table alignment and prototype agreement. Runtime signals include correct libsas phy attributes, accurate link rate from `sci_phy_linkrate()`, valid SAS address reporting, frame data visible after discovery, successful phy enable/disable/reset operations, and correct event counter propagation.
