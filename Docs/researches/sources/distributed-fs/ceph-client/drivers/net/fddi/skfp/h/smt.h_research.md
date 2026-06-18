# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/smt.h

## Purpose
`smt.h` defines SMT 7.2 frame headers, parameter structures, class/type constants, reason codes, SBA/RAF frame layouts, notification parameters, and station/port action constants.

## Important APIs, Types, And Functions
Important types are `struct smt_header`, `struct smt_para`, `struct smt_sid`, many `struct smt_p_*` parameter layouts, `struct smt_nif`, `struct smt_sif_config`, `struct smt_sif_operation`, `struct smt_ecf`, `struct smt_rdf`, and SBA RAF frame structs. Constants define SMT versions, classes (`SMT_NIF`, `SMT_RAF`, `SMT_PMF_GET`, etc.), request/reply types, parameter IDs, reason codes, sync-bandwidth commands, and swap strings.

## Control Flow
No code runs here. SMT frame builders allocate an `SMbuf`, lay out `struct smt_header` and parameters, set `p_type`/`p_len`, and send it. Parsers use parameter IDs and lengths to locate fields and optionally byte-swap based on the `SWAP_*` strings.

## State And Persistence
The header declares wire-format data only. These structs become transmitted management frames and therefore form a persistent protocol ABI with other FDDI stations.

## Dependencies And Integration Points
It depends on FDDI address types and packing macros from platform headers. `ess.c` uses RAF frame structures; SMT core and PMF/SRF code use NIF/SIF/RDF/notification parameter layouts; MIB code maps fields into these structures.

## Risks And Edge Cases
Alignment is explicitly documented: `struct smt_header` must be 32 bytes and parameters long-aligned. Flexible or variable-size parameter tails require careful length handling. `SBAPATHINDEX` is endian-specific to avoid double swapping RAF path indexes.

## Test Signals
Serialize/parse NIF, SIF config/operation, ECF, RDF, RAF allocation/change/report frames; verify parameter lengths, swap strings, endian behavior, maximum echo/info lengths, and refusal/reason code generation for unsupported or malformed frames.
