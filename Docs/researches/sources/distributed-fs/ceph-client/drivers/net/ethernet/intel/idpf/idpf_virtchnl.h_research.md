# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_virtchnl.h

## Purpose
Declares the IDPF virtchnl2 transaction interface and mailbox/vport/queue feature APIs implemented by `idpf_virtchnl.c`. It is the shared contract used by IDPF core, queue, netdev, PTP, XDP, RDMA, RSS, MAC filter, and flow steering code to issue control-plane operations.

## Important APIs, Types, And Functions
`enum idpf_vc_xn_state` defines transaction lifecycle states: idle, waiting, completed success, completed failure, shutdown, and async. `struct idpf_vc_xn` stores the completion, lock, state, reply size and destination `kvec`, async callback, opcode, ring index, and salt. `struct idpf_vc_xn_params` is the caller-facing request descriptor for `idpf_vc_xn_exec()`, including send/receive buffers, timeout, async flag, callback, and opcode.

`struct idpf_queue_ptr` and `struct idpf_queue_set` provide a typed flexible-array container for selected queue operations. The header exposes queue-set allocation plus selected queue enable, disable, and config functions. It also declares the broader virtchnl control surface: default mailbox init/deinit, VC core init/deinit, mailbox send/receive, vport create/destroy/enable/disable/init/adjust, queue register and ID initialization, queue add/delete/config/enable/disable, vector allocation/mapping, max queue accounting, MAC filters, promiscuous mode, loopback, stats, SR-IOV, RSS key/LUT, descriptor support checks, capability checks, transaction shutdown, and RDMA synchronous send.

## Control Flow
This header has no runtime control flow, but it shapes call flow across the driver. Callers allocate or prepare driver objects, populate request-specific data, and call the declared virtchnl helpers. Replies are mediated through the transaction structures and mailbox receive loop. Queue operations can use whole-vport functions or construct a selected `idpf_queue_set` for partial operations such as XDP queue handling.

## State And Persistence
The header defines in-memory transaction and queue-selection state only. Transaction state is protected by spinlocks and completions; queue sets are temporary flexible objects that point to existing queue resources. The inline `idpf_vport_deinit_queue_reg_chunks()` frees persisted queue register chunk storage from vport config.

## Dependencies And Integration Points
It includes `virtchnl2.h` and forward-declares driver types from the IDPF core. It depends on Linux kernel primitives such as `struct completion`, `spinlock_t`, `struct kvec`, `struct ethtool_rx_flow_spec`, and network/PCI-facing types supplied by including code. It is included by `idpf_virtchnl.c`, PTP virtchnl code, XDP code, and other IDPF modules needing control-plane operations.

## Risks
This header exposes async callbacks with a documented lifetime hazard: async receive buffers cannot be stack-owned if a callback needs them after send context exits. The cookie masks assume an 8-bit transaction index and 8-bit salt; changing ring length or cookie packing must remain synchronized with reply decoding. The flexible `idpf_queue_set` API trusts callers to fill `num` entries with matching queue types and valid pointers before calling config/enable/disable helpers.

## Test Signals
Compile coverage is the primary signal because type declarations and prototypes must match implementation. Runtime signals come from exercising all declared flows: mailbox init/deinit, sync and async `idpf_vc_xn_exec()`, selected queue-set operations, vport lifecycle, RSS/MAC/promisc/stats APIs, and RDMA send callback. Static analysis should flag mismatched callback lifetimes, missing locks, and incorrect queue-set type unions.
