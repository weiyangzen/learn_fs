
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cfi.h

Purpose: x86 kernel Control Flow Integrity and FineIBT support declarations.

Important APIs and control flow: documents traditional, IBT, kCFI, and FineIBT call layouts. Defines `enum cfi_mode`, `cfi_mode`, optional BHI thunk state, `CFI_OFFSET`, and CFI helpers. With `CONFIG_CFI`, `handle_cfi_failure()`, `cfi_get_offset()`, `cfi_get_func_hash()`, `cfi_get_func_arity()`, and optional `decode_fineibt_insn()` are available; without it, failure handling is a no-op and arity returns zero. `CFI_NOSEAL()` emits IBT no-seal annotations where applicable.

State, dependencies, and risks: state includes selected CFI mode, BHI toggle, generated function hashes, and patched call prefixes. Dependencies include Clang CFI, IBT, retpoline/call padding, alternatives, and bug trap handling. Risks include wrong offset calculations, trap decoding mismatches, and hard-to-debug failures in indirect calls. Test signals are CFI fault tests, objtool, IBT boot, BHI mitigation coverage, and module indirect-call tests.
