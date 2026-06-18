# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/npa.c

Purpose: Provides the CN20K mailbox handler for NPA admin-queue enqueue operations. Like the CN20K NIX shim, it delegates to the generic NPA AQ implementation through compatible structure casts.

Important APIs/types/functions: `rvu_mbox_handler_npa_cn20k_aq_enq(struct rvu *rvu, struct npa_cn20k_aq_enq_req *req, struct npa_cn20k_aq_enq_rsp *rsp)` calls `rvu_npa_aq_enq_inst()` after casting to generic `struct npa_aq_enq_req` and `struct npa_aq_enq_rsp`. The function is exported with `EXPORT_SYMBOL()`.

Control flow and integration: CN20K mailbox dispatch invokes this handler for NPA AQ requests. Generic NPA code performs actual AQ instruction construction, submission, and response handling. Exporting the symbol allows other compiled units/modules to reference the CN20K handler.

State and persistence: No local state. Effects are delegated to generic NPA AQ code and ultimately modify/read NPA hardware context state.

Dependencies: Includes CN20K `struct.h`, `../rvu.h`, and relies on `rvu_npa_aq_enq_inst()` plus layout compatibility between CN20K and generic NPA AQ request/response structs.

Risks: Unsafe if CN20K structures stop being layout-compatible with generic AQ structures. The extra `EXPORT_SYMBOL()` broadens linkage surface, so symbol availability and module ownership should be considered. There is no CN20K-specific validation in this wrapper.

Test signals: CN20K NPA aura/pool AQ operations, CN20K NPA debugfs context printing, module symbol checks, and mailbox conformance tests validate this file.
