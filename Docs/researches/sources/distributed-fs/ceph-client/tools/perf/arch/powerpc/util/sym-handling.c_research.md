# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/sym-handling.c

Purpose: PowerPC symbol normalization and probe post-processing for ELFv2 local/global entry point semantics.

Important APIs/types/functions: `arch__choose_best_symbol`, `arch__compare_symbol_names`, `arch__compare_symbol_names_n`, `arch__sym_update`, `arch__fix_tev_from_maps`, `arch__post_process_probe_trace_events`, `PPC64LE_LEP_OFFSET`.

Control flow: Chooses best symbols, compares normalized names, updates symbol entry values, and adjusts probe trace events by local entry point offsets.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on perf symbols, probe-event structures, maps, GElf symbols, and PowerPC ABI conventions.

Risks: LEP/GEP handling errors place probes at wrong instruction addresses or merge distinct symbols.

Test signals: Probe placement and symbol resolution on PPC64 ELFv1/ELFv2 binaries.

Source coverage: researched from the complete local file (144 lines, 3283 bytes).
