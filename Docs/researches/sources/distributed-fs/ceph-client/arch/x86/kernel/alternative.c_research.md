# sources/distributed-fs/ceph-client/arch/x86/kernel/alternative.c

## Purpose
`alternative.c` is the central x86 runtime and boot-time text patching engine. It applies CPU-feature alternatives, retpoline/return thunk rewrites, ENDBR sealing, FineIBT/CFI transformations, SMP lock-prefix alternatives, and live text pokes using safe temporary mappings and INT3-based synchronization. It is performance- and security-critical because it rewrites executable kernel and module text based on the actual CPU, mitigation policy, and module lifecycle.

## Important APIs, Types, and Functions
- Global state: `alternatives_patched`, `debug_alternative`, `noreplace_smp`, `x86_nops[]`, `x86_nops[]` pointer table, CFI mode state, ITS thunk page state, SMP alternative module list, `text_poke_mm`, `text_poke_mm_addr`, `text_poke_array`, and per-CPU `text_poke_array_refs`.
- Alternative patching: `apply_alternatives()`, `analyze_patch_site()`, `prep_patch_site()`, `patch_site()`, `text_poke_apply_relocation()`, `add_nop()`, `optimize_nops()`, relocation helpers, and `alt_replace_call()`.
- Spectre/return mitigation patching: `apply_retpolines()`, `patch_retpoline()`, `emit_indirect()`, `emit_call_track_retpoline()`, `apply_returns()`, `patch_return()`, and `cpu_wants_rethunk*()`.
- ITS thunk support: `its_init_mod()`, `its_fini_mod()`, `its_free_mod()`, `its_allocate_thunk()`, and `its_static_thunk()`.
- IBT/FineIBT/CFI support: `apply_seal_endbr()`, `apply_fineibt()`, `decode_fineibt_insn()`, CFI rehash/rewrite helpers, ENDBR poisoning, and hash/arity decoders.
- SMP alternatives: `alternatives_smp_module_add()`, `alternatives_smp_module_del()`, `alternatives_enable_smp()`, and `alternatives_text_reserved()`.
- Boot orchestration: `alternative_instructions()` runs INT3 selftest, disables NMI, applies paravirt caps, saves/disables IBT, rewrites CFI/retpolines/returns/call thunks/alternatives/ENDBR, optionally patches SMP locks to UP, restores IBT/NMI, sets `alternatives_patched`, and runs relocation selftest.
- Text poking: `text_poke_early()`, `text_poke()`, `text_poke_kgdb()`, `text_poke_copy_locked()`, `text_poke_copy()`, `text_poke_set()`, `smp_text_poke_batch_add()`, `smp_text_poke_batch_finish()`, `smp_text_poke_single()`, and `smp_text_poke_int3_handler()`.

## Control Flow
Boot-time patching is staged. `alternative_instructions()` first verifies INT3 call emulation, stops NMIs, sets paravirtual feature caps, disables IBT around the rewrite, applies CFI/FineIBT transformations, rewrites retpoline and return sites, finalizes ITS pages, patches call thunks, applies CPU-feature alternative instruction entries, seals ENDBR sites, restores IBT, applies UP-vs-SMP lock alternatives if only one CPU is present or allowed, restarts NMIs, and marks alternatives complete.

Alternative patching walks `.altinstructions` in order. Consecutive entries for the same instruction address are treated as a patch site; the selected replacement is the last entry whose feature predicate matches. Replacement bytes are copied into a fixed buffer, optionally direct-call adjusted, padded, relocated for relative branches/RIP-relative operands, NOP-optimized, and written with `text_poke_early()`.

Live patching after boot uses `__text_poke()` to map target text pages into a preallocated temporary mm with writable kernel permissions, copy or set bytes under disabled local IRQs, verify writes, clear PTEs, flush TLBs, and restore the previous mm. SMP multi-byte patching uses an INT3-first protocol: install breakpoints, sync cores, patch instruction tails, emit perf text-poke events, replace first bytes, sync again, and wait for all INT3 handlers to drop references. The handler emulates the old or new control-flow instruction so CPUs encountering a patch in progress continue safely.

FineIBT/CFI flow can first disable kCFI callers, optionally randomize hashes, then either re-enable kCFI or rewrite callee preambles and indirect callers for FineIBT. Decoder helpers interpret traps from FineIBT, BHI, and paranoid caller sequences so CFI violations can be reported or recovered according to policy.

## State and Persistence Behavior
Patching mutates kernel and module executable text permanently for the boot or module lifetime. `alternatives_patched` gates later consumers. ITS thunk pages are allocated, populated, then restored read/execute. SMP alternative module metadata persists while modules are loaded so lock-prefix patching can be toggled if SMP is enabled after UP patching. `text_poke_mm` is preallocated global infrastructure for later live patches. CFI mode, random seed, and BHI/paranoid flags are `__ro_after_init` policy.

## Dependencies and Integration Points
The file is tightly coupled to linker-generated sections (`__alt_instructions`, `__retpoline_sites`, `__return_sites`, `__ibt_endbr_seal`, `__cfi_sites`, `__smp_locks`), objtool output, x86 instruction decoder/evaluator, text mutex locking, module loader hooks, static calls, call thunks, CET-IBT helpers, perf text-poke events, KGDB, ftrace/static-key users of text poking, KASAN, temporary-mm code, LASS access control, NMI control, and CPU feature flags.

## Risks
- Incorrect relocation or instruction decoding can corrupt executable text and crash during boot or module load.
- Patching order matters: retpolines must be rewritten before alternatives that may alter thunks; IBT must be disabled while caller/callee contracts are inconsistent.
- Live text poking is concurrency-sensitive; missing `text_mutex`, wrong INT3 emulation, or unordered patch addresses can expose partially patched instructions.
- FineIBT/CFI transformations are byte-layout dependent and interact with ITS, BHI, retpoline, and compiler-generated CFI sequences.
- SMP lock-prefix alternatives must not patch freed init text or module ranges incorrectly.

## Test Signals
- Boot with `debug-alternative` masks to inspect alternative, return, retpoline, ENDBR, and SMP patch logs.
- Exercise module load/unload with alternatives, ITS, and SMP lock sections.
- Run the built-in INT3 and relocation selftests triggered by `alternative_instructions()`.
- Validate ftrace/static-call/jump-label/livepatch users that rely on `text_poke` and SMP batch poking.
- Test CFI modes via `cfi=off,kcfi,fineibt,debug,norand,paranoid,bhi` on supported hardware and check CFI trap decoding.
