<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/ibmvscsi_tgt.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/ibmvscsi_tgt.h

## Purpose

`ibmvscsi_tgt.h` defines the private protocol constants, state flags, command structures, target-port structures, DMA-window metadata, and hypervisor-call wrappers used by the IBM virtual SCSI target driver.

## Important APIs, Types, and Constants

- Queue sizing: `MAX_CMD_Q_PAGES`, `CRQ_PER_PAGE`, `DEFAULT_CMD_Q_SIZE`, `MAX_CMD_Q_SIZE`, `MAX_NUM_PORTS`, `MAX_H_COPY_RDMA`, and `MAX_EYE`.
- Protocol support constants include `SUPPORTED_FORMATS`, `SRP_VIOLATION`, `SCSI_LUN_ADDR_METHOD_FLAT`, `SRP_VERSION`, message word indexes, and solicited-notification bit positions.
- `struct dma_window` and `struct target_dds` store local/remote DMA window LIOBNs plus partition identity used by `H_COPY_RDMA`.
- `struct client_info` caches client SRP, partition, MAD, and OS metadata.
- `struct timer_cb` tracks the hrtimer used to retry responses when the client CRQ is full.
- `struct cmd_queue` represents the DMA-mapped CRQ ring.
- `enum cmd_type`, `struct iu_rsp`, and `struct ibmvscsis_cmd` describe command pool entries and their Target Core `se_cmd` embedding.
- `struct ibmvscsis_nexus` wraps the Target Core session; `struct ibmvscsis_tport` wraps the fabric WWN/TPG state.
- `struct scsi_info` is the core per-adapter state object with lists, flags, locks, queue metadata, request credits, client info, workqueue, completions, VIO device pointer, SRP target pool, target port, and tasklet/work items.
- State/flag macros such as `NO_QUEUE`, `WAIT_ENABLED`, `WAIT_CONNECTION`, `CONNECTED`, `SRP_PROCESSING`, `UNCONFIGURING`, `WAIT_IDLE`, `ERR_DISCONNECT`, `ERR_DISCONNECT_RECONNECT`, `ERR_DISCONNECTED`, `UNDEFINED`, `RESPONSE_Q_DOWN`, `CLIENT_FAILED`, and `PREP_FOR_SUSPEND_*` define the adapter state machine.
- Hypercall wrappers `h_copy_rdma`, `h_vioctl`, `h_reg_crq`, `h_free_crq`, and `h_send_crq` wrap `plpar_hcall_norets()`.

## Control Flow and State

The header encodes the target driver's state machine. `TARGET_STOP()` combines terminal/disconnecting states and scheduling flags so the interrupt handler can stop consuming CRQ entries. `IS_DISCONNECTING`, `DONT_PROCESS_STATE`, `BLOCK`, `PREP_FOR_SUSPEND_FLAGS`, and `PRESERVE_FLAG_FIELDS` make disconnect and suspend behavior consistent across the implementation.

Command lifecycle state moves through `free_cmd`, `schedule_q`, `active_q`, and `waiting_rsp`; each `ibmvscsis_cmd` carries the SRP IU entry, Target Core command, response tag/format/length, optional abort relationship, and flags for fast-fail or delayed send. `scsi_info` also records PHYP lock-release accounting fields to preserve state changes made while the command queue lock is dropped.

## Dependencies and Integration Points

The header includes Linux interrupt primitives, the local `libsrp.h`, Target Core types via the implementation, and SRP/VIOSRP structures through included helper headers. It is tightly coupled to `ibmvscsi_tgt.c` and not a general exported kernel interface.

## Risks and Edge Cases

- State and flag values are bit masks used in compound tests; changing values can silently alter `TARGET_STOP()` or disconnect behavior.
- `struct scsi_info` contains copied `struct device` and a VIO device pointer; lifecycle ordering must keep both valid for sysfs, DMA, IRQ, and workqueue operations.
- The `vio_iu()` macro assumes every `iu_entry` has a valid `sbuf` and SRP buffer.
- `READ_CMD` and `WRITE_CMD` use opcode low bits for fast-fail heuristics; they are intentionally narrow and should not be reused as full SCSI command classifiers.
- Hypercall wrappers hard-code the argument forms used by this driver; adding VIOCTL arguments requires checking the wrapper signature.

## Test Signals

Compile coverage should catch missing Target Core or SRP type dependencies. Runtime validation should exercise every major state and flag transition: enable, init, login, SRP processing, wait idle, reconnect, error disconnect, suspend prepare/resume, and unconfigure. Debug logs that include state/flag dumps are useful for validating that macros classify the adapter correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi_tgt/ibmvscsi_tgt.h -->
