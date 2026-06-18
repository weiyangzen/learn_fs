# sources/distributed-fs/ceph-client/tools/perf/util/machine.c

## Purpose

`machine.c` is the central perf model for a profiled address space. It owns host and guest machines, thread tables, DSO registries, kernel maps, event-driven mmap/task state, memory and branch sample resolution, callchain construction, current CPU-to-thread tracking, and kernel symbol helpers.

## Important APIs, Types, and Functions

Machine lifecycle APIs include `machine__init()`, `machine__new_host()`, `machine__new_live()`, `machine__new_kallsyms()`, `machine__exit()`, and `machine__delete()`. Multi-machine APIs include `machines__init()`, `machines__add()`, `machines__findnew()`, guest lookup, and guest processing. Thread APIs include `machine__findnew_thread()`, `machine__find_thread()`, `machine__idle_thread()`, `machine__remove_thread()`, and `machine__thread_list()`. Event processors cover COMM, NAMESPACES, CGROUP, MMAP/MMAP2, FORK, EXIT, LOST, AUX, SWITCH, KSYMBOL, BPF, TEXT_POKE, and AUX_OUTPUT_HW_ID. Kernel-map APIs include `machine__create_kernel_maps()`, `machine__destroy_kernel_maps()`, `machine__load_kallsyms()`, `machine__load_vmlinux_path()`, module creation, extra kernel maps, and x86_64 entry trampoline mapping. Resolution APIs include `sample__resolve_mem()`, `sample__resolve_bstack()`, `__thread__resolve_callchain()`, `machine__resolve_kernel_addr()`, and `machine__is_lock_function()`.

## Control Flow

Initialization creates `kmaps`, DSO/thread containers, root and mmap names, and guest placeholder threads. `machines__findnew()` resolves guest roots from `symbol_conf.guestmount` and inserts machines into a cached rb-tree. Perf event dispatch in `machine__process_event()` routes by event type. MMAP/MMAP2 events either update kernel/module maps for kernel cpumodes or create user maps and insert them into the target thread. FORK clones or initializes thread maps unless the synthesized fork-exec marker says not to; EXIT removes or marks threads. KSYMBOL and TEXT_POKE events update dynamic kernel/JIT symbol maps and DSO data caches. Kernel-map creation builds the kernel DSO, module maps, kallsyms relocation reference, extra maps, trampoline maps, and final map end fixups.

Callchain resolution first handles LBR call-stack mode when requested, then raw callchain and/or DWARF unwind depending on callchain order. It interprets context markers, resolves IPs to maps/symbols, handles parent and ignore-callee regexes, optional inline expansion, source-line caching, branch flags, loop removal, and LBR stitching across samples. Memory and branch-stack resolution use thread address-location helpers to populate `addr_map_symbol` records.

## State and Persistence Behavior

`struct machine` persists rb-tree linkage, pid, id-header size, comm behavior, root paths, `threads`, `dsos`, `kmaps`, `vmlinux_map`, kernel start cache, section ranges used for lock-function detection, current parallelism, per-CPU current TID array, private tool data, and trampoline mapping status. Event processing mutates thread comms, namespaces, maps, cgroups, kernel DSOs, dynamic symbols, and parallelism. `machine__is_lock_function()` lazily caches kernel section boundaries. Callchain processing may cache source lines and inline nodes in DSO trees and LBR stitch state in threads.

## Dependencies and Integration Points

This file is integrated with nearly every perf utility layer: callchain, branch, DSO, maps, threads, event decoding, env, evsel, hist, mem-events, mem-info, path, srcline, symbol, synthetic events, target, unwind, BPF events, cgroups, vdso, kallsyms, modules, libdw/libunwind hooks, architecture helpers, and kernel procfs/sysfs data. It is the bridge between raw perf events and higher-level report, script, annotate, mem, c2c, sched, and lock views.

## Risks and Edge Cases

Event streams may be out of order or incomplete, so thread PID repair, fork parent replacement, missing first lock events, missing maps, and zero kernel addresses are tolerated. Kernel mapping has many special cases: kcore disables later mmap processing, guest-injected mmap names may look like host names, module paths can be compressed, x86_64 PTI trampolines may lack symbols, and `kptr_restrict` may hide relocation addresses. `machine__init()` currently returns `0` even on the error path after cleanup, which is a risk if callers rely on nonzero failure. LBR stitching stores references that must be released when recycled. `sample__resolve_bstack()` assumes a branch stack exists and allocates by `bs->nr`.

## Test Signals

Good coverage includes host, live, kallsyms, and guest machine creation; synthesized MMAP/FORK streams; out-of-order fork/exit handling; kernel/module mmap with and without build IDs; ksymbol register/unregister; text poke updates; x86_64 trampoline mapping; cgroup and namespace events; current TID resizing; branch stack and memory resolution; callchains in caller/callee order with LBR, branch callstack, inline expansion, DWARF unwind, parent regex, hide-unresolved, and ignore-callee settings; and lock-function section detection.
