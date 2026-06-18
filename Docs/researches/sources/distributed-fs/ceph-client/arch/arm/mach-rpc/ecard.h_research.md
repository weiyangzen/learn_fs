# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/ecard.h

Purpose: local helper definitions for RiscPC expansion-card chunk directory parsing.

Important APIs/types/functions: defines chunk directory layouts and helper macros/functions used by `ecard.c` to interpret IDs, start offsets, lengths, loader chunks, and strings.

Control flow: no standalone flow; parsing helpers are used while walking card ROM chunk directories in `ecard_readchunk()`.

State and persistence: no state, but structures map bytes read from card ROM into kernel interpretation.

Dependencies and integration points: private to ecard implementation and card loader code.

Risks: packed/byte-level interpretation must match Acorn card ROM format. Length/offset mistakes can cause out-of-range reads or wrong card identity.

Test signals: card description lookup, loader chunk loading, and known ROM image parsing.
