# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/nix.c

Purpose: Provides the CN20K mailbox handler for NIX admin-queue enqueue operations. It adapts CN20K request/response structure types to the existing generic NIX AQ enqueue implementation.

Important APIs/types/functions: The single function is `rvu_mbox_handler_nix_cn20k_aq_enq(struct rvu *rvu, struct nix_cn20k_aq_enq_req *req, struct nix_cn20k_aq_enq_rsp *rsp)`. It casts the CN20K request and response to generic `struct nix_aq_enq_req` and `struct nix_aq_enq_rsp` before calling `rvu_nix_aq_enq_inst()`.

Control flow and integration: Mailbox dispatch routes CN20K NIX AQ messages to this handler. The handler delegates all validation, hardware AQ programming, polling, and response fill to generic NIX code, relying on layout compatibility between generic and CN20K structures for the shared prefix/operation contract.

State and persistence: No local state. It operates on RVU/NIX hardware state through the delegated generic function and fills the mailbox response supplied by the caller.

Dependencies: Includes CN20K `struct.h` and `../rvu.h`. Depends on `rvu_nix_aq_enq_inst()` accepting the casted request/response.

Risks: This is a type-adapter shim; if CN20K AQ structures diverge in incompatible ways from generic NIX AQ structures, casts become unsafe. There is no additional generation-specific validation here.

Test signals: CN20K mailbox AQ operations for SQ/CQ/RQ contexts, response decoding through CN20K debugfs printers, and build checks for handler registration validate the shim.
