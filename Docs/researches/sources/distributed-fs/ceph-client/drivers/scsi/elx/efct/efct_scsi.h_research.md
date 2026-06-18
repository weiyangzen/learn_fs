# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_scsi.h

## Purpose
`efct_scsi.h` defines the EFCT SCSI target-facing API. It provides command/data flags, SCSI completion status enums, TMF enums, SGL shape, callback typedefs, vport structure, and prototypes used by unsolicited frame parsing, LIO target glue, xport registration, and HW dispatch.

## Important APIs, Types, and Functions
Flag groups describe received FCP command direction/task attributes, data/status submission behavior, auto-response disabling, low-latency, and WQ steering/class selection. `struct efct_scsi_cmd_resp` describes status, sense, residual, and wire response length. `struct efct_vport` wraps Scsi_Host/fc_vport state and FC statistics. `enum efct_scsi_io_status` normalizes HW completion statuses. Callback typedefs model data/status completions. `enum efct_scsi_tmf_cmd` and `enum efct_scsi_tmf_resp` mirror FCP task management operations. Function prototypes cover IO alloc/free, target driver/device/session events, command/TMF receive, data/status/TMF send, abort, FC transport registration, Scsi_Host/vport lifecycle, and pending dispatch.

## Control Flow
`efct_unsol.c` uses receive prototypes for FCP and TMF frames. `efct_lio.c` uses send/abort APIs from target-core callbacks. `efct_xport.c` uses target driver and FC transport registration/device functions. `efct_scsi.c` implements the data path declared here.

## State and Persistence Behavior
The header itself stores no state, but defines the enums and flags that drive `struct efct_io` and `struct efct_scsi_tgt_io` state transitions. `struct efct_vport` persists while a Scsi_Host or NPIV vport exists.

## Dependencies and Integration Points
It includes Linux SCSI host and FC transport headers and references EFCT/EFC structures. It is one of the public contracts for cross-file EFCT target integration.

## Risks
The command direction flag naming is easy to misread: FCP write data maps to initiator-to-target and the LIO code maps that to `DMA_TO_DEVICE`. WQ steering and class masks share high bits with the flags argument, so new flags must avoid bit collisions. Status enum changes require synchronized completion translation in `efct_scsi.c` and response handling in `efct_lio.c`.

## Test Signals
Compile signature checks, command flag translation tests, status mapping tests, TMF command/response mapping, vport lifecycle tests, and WQ steering flag propagation into HW IO fields are the key signals.
