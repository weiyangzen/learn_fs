# sources/distributed-fs/ceph/src/rgw/rgw_kmip_client_impl.h

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This header declares `RGWKMIPManagerImpl`, the worker-backed concrete manager for KMIP transceiver requests. It owns a mutex/condition variable, intrusive request list, shutdown flag, and worker pointer, and implements `start()`, `stop()`, and `add_request()`. State is process-local queue/worker state; persistent effects occur through protocol operations in the implementation. Risks include heap/intrusive request ownership, referenced transceiver lifetime until completion, and `-ECANCELED` behavior during shutdown. Tests should cover start/add/stop sequencing, add while stopping, worker signalling, pending request completion on shutdown, and object lifetime assumptions.
