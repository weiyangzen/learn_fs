# sources/distributed-fs/openafs/src/rxkad/v5gen-rewrite.h

Purpose: Renames bundled Heimdal generated ASN.1 and DER symbols into an rxkad-private namespace.

Important APIs/data: Defines macros mapping `encode_*`, `decode_*`, `free_*`, `length_*`, `copy_*`, DER helper functions, and ticket-flag conversion helpers to `_rxkad_v5_*` names.

Control flow and state: Header-only preprocessor rewrite layer. It must be included before `v5gen.h`, `v5der.c`, and `v5gen.c` are compiled into `ticket5.c`.

Dependencies and integration: Generated from rxkad's v5 import workflow and documented by `README.v5`. It prevents symbol collisions with system Heimdal/MIT libraries or other OpenAFS components.

Risks: Missing a macro can export an unprefixed helper and collide at link time. Incorrect macro mapping can break generated-code calls in subtle ways. The file is mechanically generated and should stay synchronized with imported ASN.1/DER code.

Test signals: Link tests and v5 ticket encode/decode tests would catch most missing rewrites; `nm` checks described in the v5 README are useful for symbol hygiene.
