# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_els.c

## Purpose
`efc_els.c` builds, sends, completes, retries, and frees ELS, CT, and BLS discovery I/O used by libefc state machines.

## Important APIs, Types, And Functions
Allocation APIs are `efc_els_io_alloc`, `efc_els_io_alloc_size`, `efc_els_io_free`, and `_efc_els_io_free`. Completion ingress is `efc_disc_io_complete`. Send APIs include PLOGI, FLOGI, FDISC, PRLI, LOGO, ADISC, SCR, name-server RFT_ID/RFF_ID/GID_PT, LS_ACC/LS_RJT variants, CT response, BLS accept, and frame-header accept/reject helpers declared in the header.

## Control Flow And State
Each ELS request allocates a pooled `efc_els_io_req` and coherent request/response buffers, links it on `node->els_ios_list`, increments `els_req_cnt` or `els_cmpl_cnt`, fills `struct efc_disc_io`, and calls `efc->tt.send_els`. Completion callbacks translate SLI WCQE statuses into `EFC_EVT_SRRS_ELS_REQ_OK/FAIL/RJT` or `EFC_EVT_SRRS_ELS_CMPL_OK/FAIL`, retrying sequence timeouts and LS_RJT busy conditions using timers. Cleanup posts the event to the node under the common lock and drops the ELS ref, freeing DMA and possibly signaling empty I/O lists.

## Dependencies And Integration Points
The file depends on Linux DMA/timer/mempool/list primitives, FC ELS/CT structures, SLI-4 status codes, and base-driver send callbacks. It is consumed by device, fabric, namespace, and shutdown state machines.

## Risks And Test Signals
Risks include counter underflow if completions arrive after state changes, timer retry lifetime against freed ELS objects, response length overrun, and subtle misuse of request vs response DMA for CT responses. Test signals include allocation failures, all WCQE statuses, LS_RJT busy retry, local reject timeout retry exhaustion, response-length overflow, ELS disabled during shutdown, and successful cleanup causing `NODE_ACTIVE_IO_LIST_EMPTY`.
