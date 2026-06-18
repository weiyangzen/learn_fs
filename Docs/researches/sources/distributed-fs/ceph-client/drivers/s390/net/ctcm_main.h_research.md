# sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_main.h

## Purpose
`ctcm_main.h` defines the central CTCM driver data structures, constants, protocol identifiers, channel flags, CCW command values, and shared helper declarations. It is the common contract for main driver code, FSM actions, sysfs handlers, and MPC support.

## Important APIs, Types, And Functions
- Defines driver and netdev naming constants: `CTC_DRIVER_NAME`, `CTC_DEVICE_NAME`, `MPC_DEVICE_NAME`, `CTC_DEVICE_GENE`, and `MPC_DEVICE_GENE`.
- Defines channel flags and helpers such as `CHANNEL_FLAGS_READ`, `CHANNEL_FLAGS_WRITE`, `CHANNEL_FLAGS_INUSE`, `CHANNEL_FLAGS_BUFSIZE_CHANGED`, `CHANNEL_DIRECTION()`, and log flags.
- Defines supported protocols: `CTCM_PROTO_S390`, `CTCM_PROTO_LINUX`, `CTCM_PROTO_LINUX_TTY`, `CTCM_PROTO_OS390`, and `CTCM_PROTO_MPC`.
- `struct ctcm_profile` stores runtime transmit profiling counters.
- `struct channel` is the per-ccw-channel state holder for ccws, IRBs, skbs, queues, timers, MPC XID/sweep state, FSM, netdev pointer, flags, and statistics.
- `struct ctcm_priv` is the per-netdev private object containing netdev stats, busy bit, MPC group pointer, device FSM, restart timer, buffer size, and read/write channel pointers.
- Inline helpers implement netdev busy handling, channel id ordering, buffer allocation checks, and MPC protocol checks.
- `struct ll_header` defines the classic CTC link-layer header prepended to packets.

## Control Flow
The header does not execute control flow, but its structures define how control moves. `ctcm_main.c` fills `struct channel` during `add_channel()` and associates two channels with one `struct ctcm_priv` during `ctcm_new_device()`. `ctcm_fsms.c` uses channel flags to choose read vs write behavior and mutates channel/device FSM state. `ctcm_mpc.c` uses the MPC-only fields in `struct channel` and `struct ctcm_priv` to negotiate XID, sweep sequence numbers, and flow control.

## State And Persistence Behavior
All state defined here is in-memory driver state. `struct channel` owns transient DMA buffers, queued skbs, tasklets, timers, and link sequence counters. `struct ctcm_priv` owns per-interface FSM state and stats. `buffer_size` and `protocol` can be changed through sysfs before or during operation subject to validation, but they are not persisted outside the live kernel object.

## Dependencies And Integration Points
The header depends on s390 ccw headers, Linux skbuff/netdevice headers, local `fsm.h`, `ctcm_dbug.h`, and `ctcm_mpc.h`. It is included by every CTCM implementation file. Its busy helpers call `netif_stop_queue()` and `netif_wake_queue()` and are therefore part of the netdev integration contract.

## Risks
- `struct channel` mixes classic and MPC fields; changes for one protocol can accidentally affect layout, initialization, or cleanup for the other.
- The busy helper `ctcm_clear_busy()` suppresses queue wake while MPC sweep is active, so sweep state bugs can stall transmission.
- `ctcm_checkalloc_buffer()` frees and reallocates `trans_skb` if the buffer-size-changed flag is set; callers must ensure no ccw still references the old buffer.
- The macros `IS_MPC()` and `IS_MPCDEV()` assume the pointed object has a `protocol` member or is a `ctcm_priv`; misuse is unchecked.

## Test Signals
- Compile tests should catch structure and prototype drift across `ctcm_main.c`, `ctcm_fsms.c`, `ctcm_mpc.c`, and `ctcm_sysfs.c`.
- Runtime tests should validate busy-bit behavior, buffer reallocation after sysfs changes, protocol-specific MTU limits, and correct read/write channel assignment.
