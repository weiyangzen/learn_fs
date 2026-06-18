# sources/distributed-fs/ceph-client/kernel/extable.c

Purpose: provides generic kernel exception-table lookup and kernel text-address classification. It also owns `text_mutex`, the global lock for sensitive kernel text modification.

Important APIs/types/functions: `text_mutex` protects dynamic code patching. `sort_main_extable()` sorts built-in exception table entries. `search_kernel_exception_table()` searches built-in entries; `search_exception_tables()` also checks module and BPF tables. `core_kernel_text()`, `kernel_text_address()`, `__kernel_text_address()`, and `func_ptr_is_kernel_text()` classify addresses. Descriptor architectures use `dereference_function_descriptor()` and `dereference_kernel_function_descriptor()`.

Control flow: boot sorts the main exception table if build tooling did not. Fault fixup calls search built-in, module, then BPF exception tables. Address classification first checks core/init text, then with RCU/context-tracking safeguards checks modules, ftrace trampolines, kprobe slots, and BPF text.

State and persistence: exception table bounds are linker symbols; `main_extable_sort_needed` is init data; `text_mutex` is global runtime state. Tables are static kernel/module/BPF metadata and are not persisted elsewhere.

Dependencies and integration points: integrates linker sections, modules, BPF, ftrace, kprobes, architecture section helpers, context tracking, and function descriptor support. Runtime patching facilities rely on `text_mutex`.

Risks: unsorted exception tables break binary lookup. Text-address checks can run from fragile contexts such as warnings, stack dumps, idle, or CPU hotplug, so RCU/context handling must not sleep. Descriptor dereference uses nofault access for safety.

Test signals: boot exception-table sorting, uaccess/fault fixup tests, module/BPF exception tests, and stack unwinding through kprobe/ftrace/module text validate this file.
