# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc_constants.h

## Purpose

`bnx2fc_constants.h` defines firmware HSI constants for FCoE offload flows. It pairs with `57xx_hsi_bnx2fc.h`: that file defines structure layout, while this file defines version, opcodes, statuses, task states/types, timers, sizing, connection type, and firmware error codes.

## Important APIs, Types, and Definitions

HSI version is 2.1. KWQE opcodes cover function init, connection offload parts 1-4, enable, disable, destroy connection, destroy function, and statistics. KCQE opcodes cover init/destroy/stat completions, offload/enable/disable/destroy connection completions, CQ event notification, and FCoE error events. Completion statuses include success, generic error, invalid opcode, context allocation/free failure, NIC error, wrong HSI version, and parity error. Task constants define TX/RX states, task types, device/class types, timer resolution, hash-table sizing, and detailed protocol error codes.

## Control Flow

The constants drive KWQE construction, KCQE switch statements, task-context bitfield composition, and error-report recovery decisions. Firmware error bitmaps are mapped to REC/SRR or ABTS behavior in the hardware completion path.

## State and Persistence Behavior

The file stores no state. It defines legal values for firmware-visible DMA state in task contexts, queue entries, and completion records.

## Dependencies and Integration Points

It is included by `bnx2fc.h` and used across all driver objects. It depends on 57xx firmware/CNIC semantics and integrates with `fcoe_err_report_entry` processing.

## Risks and Edge Cases

Numeric drift from firmware breaks initialization, session state changes, or task completion interpretation. Tape devices get selected REC/SRR recovery, while disk/unrecognized errors fall back to ABTS. Timer resolution constants must match firmware E_D_TOV/REC_TOV expectations.

## Test Signals

Validate wrong-HSI-version rejection, all KWQE/KCQE handshakes, read/write/TMF/ELS/ABTS/cleanup task transitions, REC/SRR tape recovery, fallback ABTS, and injected firmware error reports.
