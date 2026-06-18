# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efclib.h

## Purpose
`efclib.h` defines the shared libefc object model, protocol constants, callback template, and top-level APIs used by the Emulex discovery library.

## Important APIs, Types, And Functions
It defines topology, shutdown, LS_ACC, domain event enums, `struct efc_sm_ctx`, `struct efc_domain_record`, `struct efc_nport`, `struct efc_domain`, `struct efc_remote_node`, `struct efc_node`, `struct efc_vport`, receive buffers/sequences, discovery I/O request structures, `struct libefc_function_template`, and root `struct efc`. It also declares initialization/destruction, domain/nport/node callbacks, vport management, frame dispatch, discovery I/O completion, and SCSI backend completion APIs.

## Control Flow And State
The object graph is explicit: `struct efc` owns global locks, pools, vport list, pending domain frames, callback template, and current domain; a domain owns nports and D_ID lookup; nports own remote-node lookup and service parameters; nodes own RPI state, ELS I/O lists, pending frames, login flags, timers, and state-machine context. `libefc_function_template` is the base-driver integration contract for backend node/nport notifications, mailbox issue, ELS/BLS send, and hardware sequence release.

## Dependencies And Integration Points
The header includes Linux FC protocol headers, `efc_common.h`, and SLI-4 declarations. It is the central ABI between `efct`, SLI mailbox code, libefc state machines, and SCSI initiator/target backend glue.

## Risks And Test Signals
Risks include large cross-file coupling, lock-order mistakes across `efc->lock`, `vport_lock`, pending-frame locks, and ELS locks, plus lifetime bugs around kref-owned domain/nport/node objects. Test signals include struct initialization audits, lockdep, repeated link flap/vport cycles, pool exhaustion, and backend callback paths for all `libefc_function_template` methods.
