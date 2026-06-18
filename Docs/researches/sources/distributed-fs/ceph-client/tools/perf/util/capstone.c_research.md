# sources/distributed-fs/ceph-client/tools/perf/util/capstone.c

Purpose: integrates Capstone disassembly into perf annotation and instruction printing, including optional runtime `dlopen` and x86 symbol-aware operands.

Important APIs/functions: exports `capstone__fprintf_insn_asm`, `symbol__disassemble_capstone`, and `symbol__disassemble_capstone_powerpc`. Internal wrappers abstract static vs runtime Capstone loading.

Control flow: opens a Capstone handle for the machine architecture, disassembles one instruction or an entire symbol, creates annotation lines, adds x86 RIP-relative symbol comments, and falls back to objdump by discarding partial output if full-symbol decoding fails. The PowerPC path maps ELF file offsets and stores raw 32-bit words for type sorting.

State and persistence: runtime-loading mode caches `dlopen`/`dlsym` state. Annotation lines persist under `symbol__annotation(sym)->src->source`.

Dependencies and integration: depends on Capstone, optional `dlfcn`, perf annotation, DSO readers, maps, namespaces, symbols, threads, and file map parsing. Used as an objdump alternative for perf annotate.

Risks: per-call Capstone initialization can be expensive. Runtime loading failures return generic errors. x86 detail support handles only selected operand patterns. PowerPC support is intentionally incomplete. Namespace file access and ELF offset mapping are error-prone.

Test signals: build with static Capstone, `LIBCAPSTONE_DLOPEN`, and without support; annotate x86/arm/s390/powerpc inputs; test missing library, explicit objdump fallback, unknown bytes, and namespace-backed DSOs.
