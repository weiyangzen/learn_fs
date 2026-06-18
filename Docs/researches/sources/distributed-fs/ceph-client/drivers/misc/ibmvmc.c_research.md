# sources/distributed-fs/ceph-client/drivers/misc/ibmvmc.c

## Purpose
`ibmvmc.c` implements the IBM Power Systems Virtual Management Channel misc driver. It exposes `/dev/ibmvmc` for a management application and binds a VIO device compatible with `ibm,vmc`. The driver negotiates VMC capabilities with the hypervisor through a CRQ, allocates DMA buffers per HMC session, and copies message payloads between user space and hypervisor-owned remote I/O windows with `H_COPY_RDMA`.

## Important APIs, types, and functions
The file operations are `ibmvmc_open`, `ibmvmc_close`, `ibmvmc_read`, `ibmvmc_write`, `ibmvmc_poll`, and `ibmvmc_ioctl`. Supported ioctls are `VMC_IOCTL_SETHMCID`, `VMC_IOCTL_QUERY`, and `VMC_IOCTL_REQUESTVMC`. Hypervisor-facing helpers wrap `H_COPY_RDMA`, `H_FREE_CRQ`, `H_REQUEST_VMC`, `H_REG_CRQ`, and `H_SEND_CRQ`. CRQ flow is handled by `ibmvmc_handle_event`, `ibmvmc_task`, `crq_queue_next_crq`, `ibmvmc_handle_crq`, `ibmvmc_handle_crq_init`, and `ibmvmc_crq_process`. Buffer/session helpers include `ibmvmc_add_buffer`, `ibmvmc_rem_buffer`, `ibmvmc_recv_msg`, `ibmvmc_send_msg`, `ibmvmc_send_open`, `ibmvmc_send_close`, `ibmvmc_setup_hmc`, and `ibmvmc_return_hmc`.

## Control flow
Module init registers the miscdevice, initializes global HMC slots, sanitizes module parameters, and registers the VIO driver. VIO probe reads local and remote DMA window numbers, starts a reset kthread, initializes/registers the CRQ, enables interrupts, and sends an initialization CRQ. CRQ init messages trigger a response followed by `VMC_MSG_CAP`; a valid `VMC_MSG_CAP_RESP` moves the global state to ready and clamps MTU, pool size, and HMC count. A user opens the miscdevice, calls `SETHMCID` to reserve an HMC and send `VMC_MSG_OPEN`, then reads and writes HMC protocol payloads. Incoming `VMC_MSG_SIGNAL` performs RDMA from the hypervisor window into a local DMA buffer and queues the buffer for blocking or polled reads. Writes copy from user space into a locally owned buffer, RDMA it to the hypervisor window, and signal the buffer id and length through CRQ.

## State and persistence
State is in static globals: `ibmvmc`, `hmcs[]`, `ibmvmc_adapter`, module parameters, and `ibmvmc_read_wait`. Persistent kernel-visible state lasts only while the module is loaded and the VIO device is bound. Per-HMC state tracks session number, open state, buffer metadata, a circular queue of inbound message buffer ids, and the owning file session. Reset paths close all HMCs, wake blocked readers when appropriate, free DMA buffers, and either await partner CRQ init or schedule CRQ re-registration in process context.

## Dependencies and integration points
The driver depends on PowerPC pseries VIO, PAPR hypercalls, DMA mapping APIs, tasklets, wait queues, kthreads, miscdevice infrastructure, and user-copy helpers. It integrates with user space through `/dev/ibmvmc` and with the hypervisor through CRQ and remote DMA windows described in VIO device-tree attributes.

## Risks
The global singleton design assumes one VMC adapter. Queue head/tail wrap only logs overflow, so sustained inbound traffic could overwrite unread queue state. Some helper paths call buffer selection while already holding the same HMC spinlock, which is worth auditing for lock nesting behavior. `ibmvmc_recv_msg` trusts negotiated `msg_len` sufficiently for RDMA but should remain constrained by negotiated MTU. Reset races with close/read/write are mitigated by state checks and wakeups but remain the highest behavioral risk.

## Test signals
Useful validation signals are successful miscdevice registration, VIO probe messages, CRQ init/capability exchange reaching `ibmvmc_state_ready`, `VMC_IOCTL_QUERY` returning a VMC state and DRC index, successful `SETHMCID` open response, blocking read wakeups after `VMC_MSG_SIGNAL`, and clean reset/reprobe behavior. Fault tests should cover invalid HMC indexes, invalid buffer ids, copy-to/from-user failures, partner reset (`valid == 0xff`), and module parameter clamping.
