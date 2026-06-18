<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dev.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dev.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dev.c_research.md`.

Purpose: manages one kfilnd device bound to an LNet NI: kfabric address vector/scalable endpoint setup, per-CPT endpoint allocation, peer cache initialization, debugfs files, stats reset, and teardown.

Important APIs/types/functions: `kfilnd_dev_alloc()`, `kfilnd_dev_free()`, `kfilnd_dev_post_imm_buffers()`, `kfilnd_dev_reset_stats()`, and `kfilnd_dev_get_session_key()`. The device owns `kfd_av`, `kfd_sep`, `dom`, `kfd_endpoints`, `cpt_to_endpoint`, peer cache, session-key counter, and debugfs dentries.

Control flow: allocation gets/reuses a KFI domain via `kfilnd_dom_get()`, extracts CXI NIC address, optionally obtains a Linux `struct device`, opens an AV with RX-context bits, creates and enables a scalable endpoint, allocates endpoint arrays, builds one RX/TX endpoint per NI CPT, initializes peers, marks the device initialized, stores `ni->ni_data`, rewrites the LNet NID address from NIC address, creates debugfs files, resets stats, and takes a module ref. Teardown removes debugfs, marks shutting down, cancels receive buffers, frees endpoints, destroys peers, frees arrays, closes KFI objects, puts the domain, frees the device, and drops the module ref.

State and persistence behavior: all state is per-NI runtime state. Session keys monotonically increment in an atomic for peer handshakes. Stats atomics are resettable. Endpoint and peer state are destroyed on NI shutdown.

Dependencies and integration: depends on kfabric AV/scalable endpoint APIs, CXI address and optional CXI domain ops, LNet CPT topology, endpoint/domain/peer modules, debugfs operations, and module refcounting.

Risks: resource unwinding must mirror partial allocation exactly. Device address assumptions are CXI-specific (`struct kcxi_addr`). The optional `get_device` debug message appears inverted (`if (!rc) CDEBUG("get_device failed")`). Debugfs file handles are all assigned to one member. Shutdown waits in endpoint free paths if transactions or receive buffers do not drain.

Test signals: startup/shutdown with one and multiple CPTs, allocation failure at AV/SEP/endpoint stages, provider with/without CXI ops, immediate buffer posting after startup, debugfs directory creation/removal, stats reset correctness, and module unload while NI references exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dev.c -->
