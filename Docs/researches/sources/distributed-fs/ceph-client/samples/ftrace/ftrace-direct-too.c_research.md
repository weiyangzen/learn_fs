# sources/distributed-fs/ceph-client/samples/ftrace/ftrace-direct-too.c

Purpose: second ftrace direct example that instruments `handle_mm_fault` and demonstrates trampolines for a function with multiple arguments.

Important APIs/functions: `my_direct_func(struct vm_area_struct *, unsigned long, unsigned int, struct pt_regs *)`, `my_tramp`, `ftrace_set_filter_ip`, `register_ftrace_direct`, `unregister_ftrace_direct`, and architecture stack/register save code.

Control flow: init filters `handle_mm_fault` and registers the trampoline; the trampoline passes original arguments to `my_direct_func`, which logs process name/pid and fault address. Exit unregisters.

State and persistence: ftrace ops only while module is loaded.

Dependencies and integration: depends on memory-management symbol visibility and ftrace direct support.

Risks: page fault paths are hot and sensitive. Trampoline argument preservation must match each architecture’s ABI exactly.

Test signals: load and cause page faults; inspect trace output for process and address lines; unload without lingering ftrace filter.
