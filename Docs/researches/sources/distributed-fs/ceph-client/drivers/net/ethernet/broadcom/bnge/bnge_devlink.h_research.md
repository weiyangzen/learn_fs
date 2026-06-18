# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_devlink.h

Purpose: Declares the devlink interface used by `bnge_core.c` and implemented in `bnge_devlink.c`.

Important APIs/types: `enum bnge_dl_version_type` selects fixed, running, or stored devlink version namespaces. Functions allocate/free devlink-backed `bnge_dev` and register/unregister the devlink instance.

Control flow support: Core probe calls alloc early, register after firmware data is available, unregister during teardown, and free after all users are gone.

State/persistence: No state is stored here; the header defines lifecycle entry points for devlink-private state in `struct bnge_dev`.

Dependencies/integration: Requires `struct bnge_dev` and `struct pci_dev` declarations from including context. It is part of the internal driver contract, not an external UAPI.

Risks/test signals: Signature changes must stay synchronized with core/devlink implementation. Compile-test probe/unwind paths and `devlink dev info` availability.
