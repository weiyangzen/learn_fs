# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/client.h

## Purpose
`client.h` is the internal ISHTP client contract. It defines the client object, TX ring object, default ring sizes, DMA/IPC path constants, and function declarations used by the ISHTP bus, HBM, DMA, and client-buffer layers.

## Important APIs, types, and functions
`struct ishtp_cl` holds link membership, device pointers, state/status, host and firmware client IDs, inbound/outbound flow-control credits, DMA/IPC ack bookkeeping, RX/TX lists and locks, wait queues, counters, timestamps, and caller-owned `client_data`. `struct ishtp_cl_tx_ring` wraps a list node and `struct ishtp_msg_data`. Declarations cover firmware-client lookup, send/receive dispatch, ring allocation/free, DMA buffer helpers, IO request block helpers, and `ishtp_cl_read_start()`. `ishtp_cl_cmp_id()` compares host/firmware endpoint pairs.

## Control flow and integration points
The header has no executable control flow beyond `ishtp_cl_cmp_id()`. Its fields are directly manipulated by `client.c`, `hbm.c`, `dma-if.c`, `client-buffers.c`, and higher-level ISHTP client drivers. Constants `CL_DEF_RX_RING_SIZE`, `CL_DEF_TX_RING_SIZE`, and max ring sizes define default queue capacities; `CL_TX_PATH_DEFAULT`, `CL_TX_PATH_IPC`, and `CL_TX_PATH_DMA` encode transfer policy and last-transmit path state.

## State and persistence behavior
The header defines in-memory state only. Client objects persist for the lifetime of a bound ISHTP client session, and some state is intentionally reset while buffers persist during firmware reset recovery. No on-disk persistence is present.

## Dependencies
It includes `ishtp-dev.h`, which brings device state, HBM protocol structures, and bus type declarations. It depends on Linux list, spinlock, waitqueue, ktime, GUID, and message data types indirectly through the ISHTP headers.

## Risks and edge cases
Because many fields are shared between IRQ/workqueue/client contexts, misuse of the locks declared here can produce races or credit corruption. The `uint8_t` client IDs and credit fields match the protocol but make overflow/underflow bugs easy to miss. Ring-size setters must respect the declared max sizes in callers, since this header only defines constants and does not enforce them.

## Test signals
Build coverage across ISHTP clients, lockdep stress, ring-size boundary tests, reset reconnection tests that reuse buffers, and allmodconfig builds are the main signals. Static analysis should watch for direct state writes without matching wakeups, list operations outside the proper lock, and credit underflow.
