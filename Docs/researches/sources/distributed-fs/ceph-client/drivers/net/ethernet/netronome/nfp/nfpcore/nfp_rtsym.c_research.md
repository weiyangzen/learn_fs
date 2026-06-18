# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_rtsym.c

Purpose: Reads firmware runtime symbol tables and provides lookup, bounded read/write, scalar little-endian access, and direct mapping for object symbols.

Important APIs/types/functions: `struct nfp_rtsym_entry` mirrors raw firmware entries. `struct nfp_rtsym_table` owns CPP pointer, symbol count, string table, and flexible symbol array. Public APIs include `nfp_rtsym_table_read()`, `__nfp_rtsym_table_read()`, count/get/lookup, read/write variants, scalar helpers, and `nfp_rtsym_map()`.

Control flow: Table read opens MIP, gets symtab/strtab addresses and sizes, aligns sizes, reads both from MU EMEM0, null-terminates the string table, and converts each raw entry into `struct nfp_rtsym`. Access checks symbol type and bounds, maps absolute symbols specially for reads, translates object targets/domains to CPP IDs, adjusts EMU cache direct MU addressing, and then calls CPP read/write/map helpers.

State and persistence: Runtime symbol tables are heap snapshots; mapped symbols return acquired CPP areas managed by the caller. Persistent source data lives in loaded firmware memory.

Dependencies/integration: Depends on MIP/NFFW, CPP access, MU locality, and NFP6000 target constants. NIC code uses runtime symbol mapping for firmware ABI tables such as DCB config.

Risks: String offsets are modulo `strtab_size`, preventing OOB but potentially hiding malformed tables. Negative targets other than handled EMU cache/LMEM are rejected. Write helpers reject unsupported/non-object targets but scalar ABS writes are invalid. Caller must free the symbol table with `kfree()` externally where appropriate.

Test signals: Known firmware symbol lookup, ABS read/readq behavior, object bounds checks, 4/8-byte scalar read/write, map minimum-size failure, EMU cache direct-address adjustment, and bad MIP/table size handling.
