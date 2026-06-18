# sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_libfc.h

Purpose: declares libfc-private logging controls, FC-4 provider globals, setup/teardown hooks, DDP helpers, lport/provider utility functions, and the shared SG-copy helper. It is an internal coordination header for libfc implementation files, not a userspace or low-level-driver public ABI.

Important APIs/types/functions: logging bit definitions include `FC_LIBFC_LOGGING`, `FC_LPORT_LOGGING`, `FC_DISC_LOGGING`, `FC_RPORT_LOGGING`, `FC_FCP_LOGGING`, `FC_EM_LOGGING`, `FC_EXCH_LOGGING`, and `FC_SCSI_LOGGING`. Debug macros `FC_LIBFC_DBG`, `FC_LPORT_DBG`, `FC_DISC_DBG`, `FC_RPORT_ID_DBG`, `FC_RPORT_DBG`, `FC_FCP_DBG`, `FC_EXCH_DBG`, and `FC_SCSI_DBG` gate formatted `pr_info()` output on `fc_debug_logging`. The header declares provider arrays `fc_active_prov[]` and `fc_passive_prov[]`, `fc_prov_mutex`, built-in providers `fc_rport_t0_prov`, `fc_lport_els_prov`, and `fc_rport_fcp_init`, setup functions for FCP/exchange/rport, `fc_fcp_ddp_setup()`, `fc_fcp_ddp_done()`, lport registration helpers, and `fc_copy_buffer_to_sglist()`.

Control flow: there is no executable control flow, but the macros influence runtime logging paths throughout libfc. `FC_CHECK_LOGGING()` wraps debug commands in an `unlikely()` branch. `FC_FCP_DBG()` additionally inspects the packet's active sequence to include exchange XIDs when present. The declarations encode module initialization ordering and cross-file dependencies used by `fc_libfc.c`, `fc_fcp.c`, `fc_lport.c`, and `fc_rport.c`.

State and persistence: the header declares global runtime state but owns no storage. `fc_debug_logging` is module parameter-backed in `fc_libfc.c`; provider arrays and `fc_prov_mutex` are also defined there. No persistent state is introduced by the header.

Dependencies and integration: assumes libfc structures from `scsi/libfc.h` and FC frame/exchange types are visible to including C files. It integrates private implementation units and exposes built-in FC-4 provider symbols so provider tables can be initialized centrally.

Risks and test signals: debug macros dereference fields such as `lport->host`, `pkt->rport`, and `pkt->seq_ptr`; callers should only use them with fully initialized objects. `FC_FCP_DBG()` obtains an exchange from `seq_ptr`, so use after exchange teardown would be risky. Compile coverage should include all libfc files with logging enabled, and runtime tests should toggle `debug_logging` masks while exercising lport, rport, FCP, exchange, and SCSI EH paths.
