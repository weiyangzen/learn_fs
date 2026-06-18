<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd.h

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd.h_research.md`.

Purpose: central private header for the kfabric LND. It defines constants, fail-location IDs, tunable attributes, core objects, wire protocol, transaction states/events, stats buckets, and shared externs/prototypes.

Important APIs/types/functions: defines `KFILND_VERSION`, `KFILND_IMMEDIATE_MSG_SIZE`, `KFILND_EP_KEY_BITS/MAX`, `KFILND_BASE_ADDR()`, CFS fail codes, object states, netlink tunable attributes, `struct kfilnd_immediate_buffer`, `struct kfilnd_cq`, `struct kfilnd_ep`, `struct kfilnd_peer`, `struct kfilnd_fab`, `struct kfilnd_dom`, `struct kfilnd_dev`, wire messages (`kfilnd_hello_msg`, `kfilnd_immed_msg`, `kfilnd_bulk_req_msg`, `_v2`, `kfilnd_msg`), `enum kfilnd_msg_type`, `enum tn_states`, `enum tn_events`, and `struct kfilnd_transaction`.

Control flow: not executable, but it encodes the legal transaction states and events consumed by `kfilnd_tn.c`, message layouts packed/unpacked by transaction code, endpoint/peer/device relationships, and debug/stat structures printed by debugfs.

State and persistence behavior: declares all major in-memory state. Endpoints own KFI contexts, CQs, replay queues, immediate buffers, and IDA key allocation. Peers cache KFI addresses, session keys, hello state, health state, and RCU/refcount metadata. Devices own domain/AV/scalable endpoint, CPT endpoint maps, peer cache, stats, and debugfs dentries. Transactions own LNet messages, peer refs, KFI operation context, message buffers, timeout work/timer, bulk buffer mappings, keys, status, and replay metadata.

Dependencies and integration: includes Linux kernel, libcfs, LNet, LNet RDMA, and kfabric headers (`kfi_endpoint`, `kfi_rma`, `kfi_tagged`, `kfi_cxi_ext`). Externs connect module params, debugfs operations, workqueue, tunable setup, and transaction mempool stats.

Risks: this header is a high-blast-radius ABI/contract point. Wire structs are packed and versioned; incompatible edits break interop. `KFILND_EP_KEY_BITS` limits credits and RKEY space. State/event enum ordering is baked into debug output and dispatch tables. Feature conditionals around `HAVE_KFI_SGL` split DMA mapping behavior.

Test signals: compile all kfilnd files under both SGL and non-SGL configurations, run protocol version 1/2 bulk tests, validate debugfs state names match enum tables, test max credits/key exhaustion, and use fail codes to exercise each event/state edge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd.h -->
