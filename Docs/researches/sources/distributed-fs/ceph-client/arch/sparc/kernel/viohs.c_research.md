<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/viohs.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/viohs.c

## Purpose
Implements the VIO LDC handshake helper layer used by SPARC LDOM virtual devices to negotiate protocol version, attributes, descriptor rings, ready-to-exchange state, SIDs, and LDC port lifecycle.

## Important APIs, Types, And Functions
Exported APIs include `vio_ldc_send`, `vio_link_state_change`, `vio_control_pkt_engine`, `vio_conn_reset`, `vio_validate_sid`, `vio_send_sid`, `vio_ldc_alloc`, `vio_ldc_free`, `vio_port_up`, and `vio_driver_init`. Important internal functions include `send_version`, `start_handshake`, `handshake_failure`, `send_dreg`, `send_rdx`, `process_ver`, `process_attr`, `process_dreg`, `process_dunreg`, and `process_rdx`.

## Control Flow
When LDC reports link up, the helper initializes required TX/RX descriptor-ring state based on device class and sends the first version packet. Incoming control packets pass through `vio_control_pkt_engine`, which dispatches by `stype_env`: version negotiation ACKs/NACKs select a supported version; attribute handling calls driver ops; descriptor ring registration records peer cookies or acknowledges local TX rings; RDX exchange marks the handshake complete and calls `handshake_complete`. Reset tears down RX ring state, clears version and handshake state, and disconnects LDC.

## State And Persistence
State lives in `struct vio_driver_state`: `hs_state`, `dr_state`, negotiated `ver`, local/peer SIDs, LDC channel pointer, descriptor ring states, descriptor buffer allocation, timer, lock, driver ops, device class, and version table. Descriptor buffers are allocated on RX ring registration and freed on failure, unregister, reset, or LDC free.

## Dependencies And Integration Points
Depends on `asm/ldc.h` LDC channel operations, `asm/vio.h` packet layouts and constants, Linux timers/spinlocks/slab, and class-specific VIO drivers that implement attribute and completion callbacks.

## Risks And Edge Cases
Handshake state ordering is strict; out-of-order control packets force reset. `vio_ldc_send` spins with microsecond delays on `-EAGAIN`, so long stalls are bounded but possible. SID validation includes a Solaris disk-server workaround that intentionally treats disk clients differently. Descriptor-ring cookie counts must fit the stack union.

## Test Signals
Signals include LDC link-up/reset events, version ACK/NACK fallback, vnet/vdisk descriptor ring registration, RDX completion callbacks, invalid SID packet rejection, connection retry timer behavior, and cleanup of `desc_buf` across resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/viohs.c -->
