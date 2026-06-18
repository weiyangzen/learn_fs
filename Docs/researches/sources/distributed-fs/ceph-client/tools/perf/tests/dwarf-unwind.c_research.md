# sources/distributed-fs/ceph-client/tools/perf/tests/dwarf-unwind.c

Purpose: `dwarf-unwind.c` tests user-space DWARF unwinding by constructing a known call chain and verifying resolved symbols in both caller and callee order.

Important APIs and state: global non-static functions are deliberately retained for symbol lookup. `unwind_entry` validates each frame against an expected stack. `test_dwarf_unwind__thread` captures an arch unwind sample and calls `unwind__get_entries`. The suite is `"Test dwarf unwind"`.

Control flow: `test__dwarf_unwind` enables DWARF callchain mode, creates a live machine and kernel maps, finds the current thread, and calls a chain of noinline functions. The deepest function invokes `bsearch` through a volatile function pointer so unwinding crosses libc and calls a comparator. The comparator runs unwinding once in caller order and again in callee order.

State and persistence: state is process-local machine/thread/sample data. Allocated user stack and register sample buffers are freed.

Dependencies, integration, risks, and tests: it depends on architecture-specific `test__arch_unwind_sample`, unwind support, symbols, frame retention despite optimization, and available maps. Risks include compiler tail-call optimization, stripped symbols, missing unwind backend, and libc differences. Test signals are exactly `MAX_STACK` resolved frames matching the expected function sequence in both orders.
