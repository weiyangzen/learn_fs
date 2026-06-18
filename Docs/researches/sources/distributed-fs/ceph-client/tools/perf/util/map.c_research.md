# sources/distributed-fs/ceph-client/tools/perf/util/map.c

## Purpose

`map.c` implements perf's refcounted mapping object, which connects an address range to a DSO and translates between runtime IPs, DSO-relative addresses, and objdump addresses. It handles user maps, kernel maps, anonymous maps, Android library remapping, vdso namespace handling, symbol loading, and formatted map output.

## Important APIs, Types, and Functions

Constructors are `map__new()` for mmap events and `map__new2()` for known DSOs such as kernel/modules. Lifetime APIs are `map__clone()`, `map__put()`, `map__delete()`, and internal `map__exit()`. Symbol APIs include `map__load()`, `map__find_symbol()`, `map__find_symbol_by_name_idx()`, `map__find_symbol_by_name()`, `map__fixup_start()`, and `map__fixup_end()`. Address conversion APIs are `map__rip_2objdump()`, `map__objdump_2mem()`, and `map__objdump_2rip()`. Classification helpers identify kernel maps, extra kernel maps, BPF programs/images, out-of-line code, modules, anonymous/no-DSO memory, vdso, and entry trampolines.

## Control Flow

`map__new()` allocates a refcounted map, classifies the filename, obtains namespace info from the thread, rewrites executable anonymous/no-DSO maps to `/tmp/perf-<pid>.map`, rewrites Android library paths from environment variables, handles vdso maps by clearing namespace setns requirements and using `machine__findnew_vdso()`, otherwise finds or creates a DSO by id. It initializes map bounds, pgoff, DSO reference, protection, flags, and mapping type; anonymous/no-DSO maps become identity mappings and non-exec DSOs are marked loaded. Build IDs may be copied from a header DSO with the same name. Symbol lookup loads the DSO lazily and then searches by address or name. Address conversion branches on `dso__adjust_symbols()`, ET_REL, user/kernel DSO space, pgoff, text offset, relocation, and entry trampoline remapping.

## State and Persistence Behavior

Each map stores start, end, pgoff, reloc, DSO reference, refcount, prot, flags, mapping type, and warning/private/hit bits. Kernel DSOs allocate trailing `struct kmap` storage. Maps own a DSO reference until final put. Loading a map mutates DSO loaded/symbol state. `map__srcline()` and `map__fprintf_srcline()` depend on DSO source-line caches.

## Dependencies and Integration Points

The implementation depends on DSO, namespace, srcline, symbol, thread, vdso, machine, Linux mman flags, and perf debug/config globals. It is used by `maps.c`, `machine.c`, annotation/disassembly code, callchain resolution, perf report/script output, and any code that needs reliable address translation.

## Risks and Edge Cases

Android remapping depends on `APP_ABI`, `APK_PATH`, `NDK_ROOT`, and `APP_PLATFORM`. Executable anonymous maps are redirected to JIT map files only when namespace info is available. VDSO maps must not use container setns. The DSO deleted-name check is fragile around `(deleted)` suffix handling. Address conversion is easy to break because ET_EXEC, ET_DYN, ET_REL, kernel, kcore, and trampoline paths differ. `map__contains_symbol()` compares unmapped symbol start against runtime range and depends on correct mapping type.

## Test Signals

Tests should cover user shared libraries, ET_EXEC, ET_DYN, ET_REL, kernel maps, modules, vdso, anonymous executable JIT maps, Android path rewrites, BPF image/program classification, symbol load failures, map clone/refcount behavior, source-line formatting, and round trips through `rip_2objdump`, `objdump_2mem`, and `objdump_2rip`.
