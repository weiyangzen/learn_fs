# sources/distributed-fs/ceph-client/arch/arm64/kernel/module-plts.c

Purpose: Sizes, creates, and emits arm64 module PLT entries for out-of-range branches, ftrace trampolines, and ADRP erratum veneers.

Important APIs and state: `get_plt_entry()` builds an ADRP/ADD/BR sequence using x16. `module_emit_plt_entry()` emits or reuses branch PLTs. `module_emit_veneer_for_adrp()` handles ARM64 erratum 843419 when enabled. `module_frob_arch_sections()` finds `.plt`, `.init.plt`, ftrace trampoline sections, sorts branch relocations, counts required entries, and resizes sections.

Control flow: relocations are partitioned so branch relocations needing PLTs are grouped and sorted, enabling duplicate detection. `count_plts()` counts branch PLTs and optional ADRP veneers, adjusts alignment to avoid vulnerable ADRP offsets, and adds slack for skipped unsafe slots. Emit functions choose core/init PLT section based on relocation target, skip forbidden ADRP offsets, and enforce max-entry bounds.

Dependencies and integration: used by module loader and `module.c` relocation fallback. Integrates with ftrace, ARM64 erratum 843419 capability, ELF section metadata, instruction encoders, and module init/core memory layout.

Risks and test signals: risks are undercounting PLTs, duplicate detection errors, forbidden ADRP placement, module section alignment changes, and ftrace trampoline absence. Test with large modules placed far from core kernel, ftrace-enabled modules, erratum 843419 configs, init text relocations, and module load/unload stress.
