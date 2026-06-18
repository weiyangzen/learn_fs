# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_mip.c

Purpose: Locates and reads the firmware MIP metadata structure, which points to runtime symbol and string tables.

Important APIs/types/functions: `struct nfp_mip` mirrors firmware metadata including signature, version, symbol table address/size, string table address/size, and name/toolchain. `nfp_mip_open()` returns a copied MIP, `nfp_mip_close()` frees it, `nfp_mip_name()`, `nfp_mip_symtab()`, and `nfp_mip_strtab()` expose fields.

Control flow: `nfp_mip_open()` allocates a MIP buffer, opens NFFW info, finds the first loaded firmware MIP location, reads it via CPP, validates signature/version, terminates the name, and returns it. Errors close the NFFW resource and free memory.

State and persistence: The returned MIP is a heap copy of firmware metadata. Device firmware owns the persistent source; the kernel only snapshots it.

Dependencies/integration: Depends on `nfp_nffw_info_open()`/`nfp_nffw_info_mip_first()` and CPP reads. `nfp_rtsym.c` uses this file to locate runtime symbol tables.

Risks: Only the first loaded firmware MIP is used. Unsupported MIP versions or bad signatures disable runtime symbol access. Table addresses are trusted after MIP validation and are later read from MU.

Test signals: Load firmware with known MIP, verify name and table addresses, test missing/bad MIP signatures, and confirm NFFW lock release on error.
