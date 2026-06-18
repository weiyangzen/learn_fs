# sources/distributed-fs/ceph-client/kernel/gcov/clang.c

## Purpose
`clang.c` adapts LLVM/Clang's `llvm_gcov_init()`/`llvm_gcda_*()` callback model to the kernel gcov debugfs infrastructure. LLVM does not expose a GCC-style stable `gcov_info` object, so this file builds a kernel-local `gcov_info` list while compiler-rt calls back through start-file, function, and arc emission hooks.

## Important APIs, types, and functions
The file defines private `struct gcov_info` and `struct gcov_fn_info` layouts for Clang coverage, stores registered objects in `clang_gcov_list`, and uses `current_info` as transient callback context. Exported compiler hooks are `llvm_gcov_init()`, `llvm_gcda_start_file()`, `llvm_gcda_emit_function()`, `llvm_gcda_emit_arcs()`, `llvm_gcda_summary_info()`, and `llvm_gcda_end_file()`. Generic gcov integration is provided through `gcov_info_filename()`, `gcov_info_version()`, `gcov_info_next()`, `gcov_info_link()`, `gcov_info_unlink()`, `gcov_info_within_module()`, `gcov_info_reset()`, compatibility/add/dup/free helpers, and `convert_to_gcda()`.

## Control flow
`llvm_gcov_init()` allocates a new info object, links it under `gcov_lock`, sets `current_info`, calls LLVM's writeout callback, then emits a `GCOV_ADD` event if debugfs event replay is enabled. The callback sequence populates filename/version/checksum, appends one function record per `llvm_gcda_emit_function()`, and attaches counter arrays through `llvm_gcda_emit_arcs()`. Reads from debugfs later call `convert_to_gcda()`, which serializes the stored records into a `.gcda` stream: header, function tags, counter tag, and 64-bit counter values.

## State and persistence
Registered Clang coverage objects persist in `clang_gcov_list` for the lifetime of the module/object that registered them. Function counter pointers normally reference compiler-generated storage, while duplicated info objects deep-copy filenames and counter arrays for unloaded-module persistence in `fs.c`. `current_info` is valid only during the writeout callback. There is no disk persistence here; debugfs readers synthesize gcda bytes on demand.

## Dependencies and integration points
This file depends on `gcov.h`, the shared `gcov_lock` and event mechanism from `base.c`/`fs.c`, Linux list and allocation helpers, module address range checks via `within_module()`, and the compiler-rt LLVM gcov callback ABI. It intentionally exposes the same generic gcov helper API as the GCC backend so `fs.c` can operate without knowing the compiler-specific layout.

## Risks and test signals
Risks include callback ordering assumptions, silent loss of function records on allocation failure, `llvm_gcda_emit_arcs()` assuming a function was just appended, compatibility checks that compare checksums but not counter counts before addition, and lifetime hazards because live counter arrays are not owned by this file. Test signals include boot/module coverage with Clang, unload persistence with `gcov_persist=1`, reset clearing live counters, debugfs gcda streams accepted by `gcov`, incompatible reload warnings, and failure injection around function/counter duplication.
