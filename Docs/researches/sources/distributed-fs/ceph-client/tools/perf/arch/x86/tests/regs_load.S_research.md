# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/regs_load.S

Purpose: This assembly file implements `perf_regs_load`, a test helper that snapshots general-purpose registers into a caller-provided `u64` register array. It is used by x86 perf unwind/register tests to seed expected register state.

Important APIs, types, and functions: The exported symbol is `perf_regs_load`, declared by the x86 perf registers header and defined with `SYM_FUNC_START`/`SYM_FUNC_END`. The file defines byte offsets for AX, BX, CX, DX, SI, DI, BP, SP, IP, FLAGS, segment registers, and x86-64-only R8 through R15. It has separate implementations under `HAVE_ARCH_X86_64_SUPPORT` and the 32-bit fallback.

Control flow: On x86-64, `%rdi` points at the destination array. The function stores all general registers, records the caller stack pointer as `8(%rsp)` to exclude the helper call frame, records the return address from `0(%rsp)` as IP, zeroes flags and segment slots, stores R8-R15, and returns. On 32-bit, it saves the incoming destination pointer from the stack into `%edi`, handles `%edi` specially via a push/pop sequence so the original DI value is captured, stores 32-bit registers into 64-bit-spaced slots, records stack and return IP, zeroes unavailable metadata slots, and returns.

State and persistence: The function writes only to the destination register buffer supplied by the caller. It clobbers scratch registers as part of the snapshot process and intentionally records an adjusted SP/IP view. No persistent state exists.

Dependencies and integration points: It depends on Linux `linkage.h` symbol macros and on the register-index ABI expected by `arch/x86/include/perf_regs.h` and dwarf-unwind tests. The `.note.GNU-stack` section declares a non-executable stack for the assembled object.

Risks: Offset constants must stay aligned with perf's register numbering. The helper is ABI-sensitive: changing stack adjustment from `8(%rsp)` or `4(%esp)` would change unwind-test expectations. The 32-bit path's DI save/restore is easy to break because `%edi` is both an input pointer and a register under test.

Test signals: x86 `perf test` dwarf unwind/register tests using `perf_regs_load()` should pass on both 32-bit and 64-bit builds. Linker warnings about executable stack would indicate the GNU-stack marker was lost.
