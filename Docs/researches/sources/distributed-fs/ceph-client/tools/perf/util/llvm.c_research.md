# sources/distributed-fs/ceph-client/tools/perf/util/llvm.c

## Purpose

`llvm.c` is perf's optional LLVM-backed address-to-source and disassembly adapter. When `HAVE_LIBLLVM_SUPPORT` is enabled it resolves source lines and inline frames through helper APIs and disassembles symbol bytes without spawning objdump. When LLVM support is absent the public entry points return failure so existing objdump or non-inline paths can be used.

## Important APIs, Types, and Functions

The exported APIs are `llvm__addr2line()` and `symbol__disassemble_llvm()`. `llvm__addr2line()` wraps `llvm_addr2line()`, optionally converts returned `llvm_a2l_frame` records into perf inline symbols with `new_inline_sym()`, `srcline_from_fileline()`, and `inline_list__append()`, and frees frame strings with `free_llvm_inline_frames()`. `symbol__disassemble_llvm()` reads symbol bytes via `dso__read_symbol()`, initializes all LLVM targets once in `init_llvm()`, creates a disassembler for x86 or a generic `<arch>-linux-gnu` triplet, and emits `struct disasm_line` records into `symbol__annotation(sym)->src->source`. `symbol_lookup_storage` is callback scratch state used by `symbol_lookup_callback()` to remember branch and PC-relative data references observed by LLVM.

## Control Flow

Address-to-line flow is straight-line: call LLVM helper, return on no inline frames, otherwise append each inline frame to the caller-provided `inline_node`. Disassembly first rejects explicit `objdump_path`, reads the symbol from the DSO/map, creates and configures the LLVM context, emits a function header line, then loops over instruction bytes with `LLVMDisasmInstruction()`. For each instruction it uses callback-collected addresses to append code or data symbol annotations from `llvm_name_for_code()` and `llvm_name_for_data()`, expands tabs, asks LLVM for a file/line for the current PC, and adds a disassembly line. All error exits dispose the LLVM context and free temporary buffers.

## State and Persistence Behavior

State is transient except for annotation lines appended to the symbol annotation tree and inline nodes cached by callers. LLVM target initialization is protected by a static boolean and persists process-wide. The function owns `code_buf`, `line_storage`, `args->fileloc`, and returned inline-frame strings. It sets fields in `annotate_args` while constructing each output line, so callers must treat that object as mutable during disassembly.

## Dependencies and Integration Points

This file depends on perf annotation, DSO, map, srcline, namespace, and symbol helpers, plus LLVM C disassembler APIs under `HAVE_LIBLLVM_SUPPORT`. It integrates with perf annotate/disassembly output, inline callchain presentation, source-line reporting, and architecture selection through `args->arch`. The x86 path handles 32-bit versus 64-bit code using the DSO read result; aarch64 requests `+all` CPU features.

## Risks and Edge Cases

LLVM callbacks deliberately return `NULL` and suppress LLVM's own symbol text because LLVM adds quotes around returned names. Incorrect callback state would lose branch/data annotations. `LLVMSetDisasmOptions()` order matters because the asm-printer variant can reset `PrintImmHex`. `llvm_addr2line()` is called with `filename` during disassembly but with `dso_name` in the public addr2line API; path and namespace mismatches can affect source lookup. A zero instruction length aborts the whole disassembly. Without LLVM support both public paths fail cleanly.

## Test Signals

Useful tests include building with and without `HAVE_LIBLLVM_SUPPORT`, `perf annotate --disassembler=llvm` on x86 and aarch64 binaries, branch and PC-relative load annotations, inline frame expansion, Intel syntax selection, and fallback behavior when `objdump_path` is set. Leak checks should cover early failures after partial inline-frame or disassembly-line creation.
