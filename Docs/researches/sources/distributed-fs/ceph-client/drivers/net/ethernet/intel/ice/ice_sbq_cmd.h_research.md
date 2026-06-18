# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sbq_cmd.h

## Purpose

`ice_sbq_cmd.h` defines the sideband queue command ABI used by software and firmware to read and write neighboring devices such as PHY and CGU blocks. In this work item it is directly consumed by `ice_ptp_hw.c` for PHY register access and by common code implementing `ice_sbq_rw_reg`.

## Important APIs And Types

`enum ice_sbq_opc` defines sideband queue admin opcodes for neighbor device request and event descriptors. `struct ice_sbq_cmd_desc` is the indirect, non-posted sideband command descriptor with flags, opcode, data length, return value, cookie fields, length union, reserved bytes, and address high/low fields. `struct ice_sbq_evt_desc` represents sideband events.

`enum ice_sbq_dev_id` names destination devices used by the driver: primary PHY, CGU, peer PHY, and peer CGU. `enum ice_sbq_msg_opcode` distinguishes register read and write messages. `ICE_SBQ_MSG_FLAGS` and `ICE_SBQ_MSG_SBE_FBE` define message flag defaults. `struct ice_sbq_msg_req` and `struct ice_sbq_msg_cmpl` describe request/completion payloads, while `struct ice_sbq_msg_input` is the internal normalized input consumed by `ice_sbq_rw_reg`.

## Control Flow Role

The header has no executable code. Runtime flow is: a caller fills `struct ice_sbq_msg_input` with destination device, opcode, split address, and data; `ice_sbq_rw_reg` builds a sideband descriptor and request; firmware completes the request and read data is returned through the same input structure. PTP code uses this repeatedly for E82x, E810, and ETH56G register access.

## State And Persistence Behavior

No persistent state is stored here. The structs define transient command and event buffers exchanged with firmware. Multi-byte fields are explicitly little-endian where they cross the firmware ABI, so callers and descriptor builders must preserve endian conversion rules.

## Dependencies And Integration Points

The header is included by `ice_type.h`, `ice_common.c`, and PTP hardware code through common driver headers. It is tightly coupled to `ice_sbq_rw_reg` in `ice_common.c`, firmware/admin queue conventions, and device IDs used by PTP and CGU access.

## Risks And Edge Cases

This is an ABI header, so field sizes, ordering, and endianness are critical. Incorrect destination device selection can send a valid transaction to the wrong PHY or CGU, especially on dual-complex E825C where peer device IDs matter. Read/write opcode confusion can corrupt hardware registers. Callers must split 32-bit addresses into low/high fields consistently.

## Test Signals

Test signals include successful sideband reads/writes to known PHY/CGU registers, correct error propagation from firmware command return values, validation that peer PHY/CGU IDs work on multi-PHY devices, and static build checks that descriptor sizes and field types match firmware expectations.
