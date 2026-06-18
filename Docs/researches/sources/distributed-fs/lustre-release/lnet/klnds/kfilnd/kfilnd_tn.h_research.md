<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_tn.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_tn.h

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_tn.h_research.md`.

Purpose: declares the transaction subsystem interface consumed by LNet entry points, CQ processing, endpoints, and debugfs.

Important APIs/types/functions: `kfilnd_tn_process_rx_event()`, `kfilnd_tn_free()`, `kfilnd_tn_alloc()`, `kfilnd_tn_alloc_for_hello()`, `kfilnd_tn_event_handler()`, `kfilnd_tn_cleanup()`, `kfilnd_tn_init()`, and `kfilnd_tn_set_buf()`.

Control flow: send/receive paths allocate and initialize transactions, CQs deliver events through the event handler, endpoint replay replays saved events, and module init/exit initializes/cleans mempools.

State and persistence behavior: no state is declared here, but API ownership is important: after the first event handler call, the transaction subsystem owns lifetime until finalization.

Dependencies and integration: includes `kfilnd.h` for transaction, device, peer, and bio_vec/LNet types.

Risks: callers must not use a transaction after handing it to the event handler unless a specific LNet callback contract says it remains valid. `key` argument naming means memory-region key allocation, not auth key.

Test signals: compile all users, verify transaction ownership in send/receive paths, and run event replay plus cleanup with outstanding transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_tn.h -->
