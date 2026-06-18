## sources/distributed-fs/ceph-client/fs/smb/smbdirect/internal.h

Purpose: Defines SMBDirect module-internal declarations and global state shared across implementation files. It establishes the module symbol namespace, logging prefix, global workqueue/device container, internal device wrapper, cleanup scheduling macros, and prototypes for non-exported cross-file helpers.

Important APIs and types: `struct smbdirect_module_state` holds the global mutex, six workqueue pointers (`accept`, `connect`, `idle`, `refill`, `immediate`, `cleanup`), and the RDMA device list protected by an rwlock. `struct smbdirect_device` links an `ib_device` into the global list with a copied device name. Cleanup macros wrap `__smbdirect_socket_schedule_cleanup()` with call-site function/line and optional forced status. Prototypes cover socket initialization/destruction, connection QP/mempool/send/recv/MR helpers, accept negotiation, and device init/exit.

Control flow: This header has no runtime control flow, but it shapes cross-file control by allowing accept/connect/listen/device/main code to call shared connection and socket internals while keeping public API declarations in external headers.

State and persistence: Declares the global `smbdirect_globals`, whose storage is in `main.c`. State remains volatile module memory: workqueues, device list, locks, and socket resources. No persistent state is introduced.

Dependencies and integration points: Includes `<linux/smbdirect.h>`, `pdu.h`, mutex support, and finally `socket.h` so all internal code sees the full socket layout. It integrates the SMBDirect module with Linux RDMA/IB types and the rest of fs/smb transport code.

Risks and edge cases: Since this header exposes the full internal socket helper surface to every implementation file, changes to prototypes or global state have wide compile-time and behavioral impact. Cleanup macros capture local `__func__`/`__LINE__`; misuse outside a real socket error path could force unwanted disconnect. Include ordering matters because `socket.h` depends on definitions and PDU types.

Test signals: Build coverage is the main signal: all SMBDirect implementation files must compile after prototype or struct changes. Runtime smoke tests should verify that all workqueue pointers are initialized before any socket is initialized and that cleanup macros produce correct status transitions.
