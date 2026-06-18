# sources/distributed-fs/ceph-client/arch/x86/lib/retpoline.S

## Purpose
This file supplies x86 indirect branch and return thunks for Spectre/Retbleed/SRSO/ITS mitigations. It contains compiler-visible thunk symbols, alternative instruction sequences selected by CPU feature bits, and special return-untraining sequences with strict alignment requirements.

## Important APIs, Types, and Functions
Generated symbols include `__x86_indirect_thunk_<reg>` for every general register, optional `__x86_indirect_call_thunk_<reg>` and `__x86_indirect_jump_thunk_<reg>` for call-depth tracking, optional `__x86_indirect_its_thunk_<reg>` and paranoid ITS thunks, `entry_untrain_ret`, `call_depth_return_thunk`, `its_return_thunk`, `srso_alias_untrain_ret`, `srso_alias_safe_ret`, `srso_return_thunk`, `retbleed_return_thunk`, and the compiler magic symbol `__x86_return_thunk`. Macros `POLINE`, `RETPOLINE`, `THUNK`, `CALL_THUNK`, `JUMP_THUNK`, and `ITS_THUNK` compose the thunks.

## Control Flow
The base thunk array emits one entry per register. Depending on alternatives, each thunk runs a classic retpoline, an LFENCE plus indirect jump, or a direct indirect jump when retpoline is not needed. RETHUNK code emits return thunks and untraining sequences: SRSO paths use aliasing or MOVABS-style safe returns, Retbleed paths use aligned byte sequences that intentionally decode differently when entered at different points, and call-depth tracking stuffs the return stack when the per-CPU depth counter reaches zero. `__x86_return_thunk` is a boot/module-init target expected to be patched by `apply_returns()`.

## State and Persistence
Runtime state is mostly code text and alternative-patched instruction bytes. Call-depth tracking also uses per-CPU `__x86_call_depth`. The file exports thunk symbols so modules and compiler-generated code can reference stable mitigation entry points.

## Dependencies and Integration Points
It depends on x86 alternative patching, CPU feature bits, objtool/unwind hints, IBT annotations, per-CPU assembly, compiler options such as `-mindirect-branch=thunk-extern` and `-mfunction-return=thunk-extern`, module symbol exports, and mitigation Kconfig choices. It is tightly integrated with boot-time return patching and entry code.

## Risks and Test Signals
Risks are high because alignment, symbol names, annotations, and byte layouts are mitigation contracts. A bad change can break speculation protections, unwinding, module linkage, objtool validation, or boot. Test signals include objtool success, absence of unpatched `__x86_return_thunk` warnings, CPU-feature alternative coverage, module loading with thunk references, mitigation selftests/boot logs, and performance/regression checks on affected Intel and AMD families.
