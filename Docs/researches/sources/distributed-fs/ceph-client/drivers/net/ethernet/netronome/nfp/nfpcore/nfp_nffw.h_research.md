# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nffw.h

Purpose: Declares firmware metadata, MIP, and runtime symbol table APIs shared across nfpcore and NIC code.

Important APIs/types/functions: Declares `nfp_nffw_info_*`, `nfp_mip_*`, `enum nfp_rtsym_type`, `struct nfp_rtsym`, `struct nfp_rtsym_table`, runtime symbol lookup/read/write/map APIs, and target sentinel values such as `NFP_RTSYM_TARGET_LMEM` and `NFP_RTSYM_TARGET_EMU_CACHE`.

Control flow/state: Header-only API contract. Symbol tables are heap snapshots returned by implementation files; mapped symbols return acquired CPP areas that callers must release.

Dependencies/integration: Used by firmware metadata readers, PF/app code, and DCB mapping through runtime symbols.

Risks: Callers must respect object lifetimes and symbol bounds. Special negative target encodings are not universally mappable; implementation rejects unsupported targets.

Test signals: Compile consumers, read runtime symbol tables after firmware load, map known symbols, and validate scalar read/write helpers.
