# sources/distributed-fs/ceph-client/include/asm-generic/vmlinux.lds.h

Purpose: central macro library used by architecture linker scripts to construct `vmlinux` sections, boundaries, init/exit ranges, percpu layout, debug sections, discard lists, and feature-specific tables.

Important APIs/types/functions: macro families include `TEXT_MAIN`, `DATA_MAIN`, `RO_DATA`, `RW_DATA`, `INIT_TEXT_SECTION`, `INIT_DATA_SECTION`, `BSS_SECTION`, `PERCPU_SECTION`, `EXCEPTION_TABLE`, `NOTES`, `MODINFO`, `BUG_TABLE`, `ORC_UNWIND_TABLE`, `MCOUNT_REC`, `FTRACE_EVENTS`, `TRACE_SYSCALLS`, `LSM_TABLE`, `OF_TABLE`, `ACPI_PROBE_TABLE`, `KERNEL_DTB`, `KUNIT_TABLE`, `DISCARDS`, and `COMMON_DISCARDS`.

Control flow: there is no C runtime flow; the "flow" is link-time expansion. Architecture linker scripts combine these macros to order input sections, emit start/stop symbols, align special regions, keep required tables, and discard sections that must not remain in the final kernel image.

State and persistence: defines persistent kernel image layout and exported section boundary symbols such as initcall ranges, percpu ranges, tracing metadata, exception tables, and BSS boundaries. These symbols are consumed at boot and by runtime subsystems.

Dependencies and integration points: depends heavily on `CONFIG_*` feature gates and linker-script syntax. Integrated with initcalls, ftrace, jump labels, static calls, BPF raw tracepoints, LSM, OF/ACPI probing, KUnit, firmware loader built-ins, BTF, ORC unwinder, module metadata, and percpu allocator setup.

Risks: small ordering or alignment mistakes can break boot, initcall ordering, exception fixups, module metadata, unwinding, percpu offsets, or security hardening. Feature-gated sections must match producer annotations or data can be discarded or orphaned. Linker differences make orphan-section and KEEP semantics important.

Test signals: full kernel link tests for multiple architectures/configurations, boot tests with tracing/ftrace/static-call/percpu enabled, `readelf`/`objdump` inspection of section boundaries, initcall ordering checks, and linker orphan warnings.
