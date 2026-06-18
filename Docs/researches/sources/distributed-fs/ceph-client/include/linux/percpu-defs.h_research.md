<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu-defs.h -->
# sources/distributed-fs/ceph-client/include/linux/percpu-defs.h

## Purpose
Provides the low-level declaration, definition, pointer translation, and scalar operation macros for per-CPU variables. It is intended for inclusion from architecture percpu headers and avoids cyclic dependencies with `linux/percpu.h`.

## Important APIs, Types, And Functions
- Declaration/definition macros include `DECLARE_PER_CPU_SECTION`, `DEFINE_PER_CPU_SECTION`, `DECLARE_PER_CPU`, `DEFINE_PER_CPU`, cache-hot/shared-aligned/page-aligned/read-mostly/decrypted variants, and `EXPORT_PER_CPU_SYMBOL*`.
- Pointer accessors include `per_cpu_ptr()`, `raw_cpu_ptr()`, `this_cpu_ptr()`, `per_cpu()`, `get_cpu_var()`, `put_cpu_var()`, `get_cpu_ptr()`, and `put_cpu_ptr()`.
- Type safety is enforced through `__verify_pcpu_ptr()` and `PERCPU_PTR()`.
- Size-dispatch helpers call architecture-provided 1/2/4/8-byte operations or trigger `__bad_size_call_parameter()`.
- Raw, checked, and protected operation families include `raw_cpu_read/write/add/and/or/xchg/cmpxchg/try_cmpxchg`, `__this_cpu_*`, and `this_cpu_*` plus inc/dec/sub return variants.

## Control Flow
Declarations place variables into specific per-CPU ELF sections. Accessors translate a per-CPU symbol to a CPU-specific address using `per_cpu_offset()` or arch raw CPU pointer helpers. Operation macros verify percpu pointer types, dispatch by operand size, and invoke arch-specific primitives. `get_cpu_*` disables preemption until the matching `put_cpu_*`.

## State And Persistence
Per-CPU variables are persistent kernel memory replicated per CPU or per allocation unit. Section naming and alignment control layout, locality, and cache behavior. Weak-definition logic for certain module architectures adds hidden dummy symbols to enforce scope and uniqueness.

## Dependencies And Integration Points
Depends on `CONFIG_SMP`, module settings, architecture percpu support, preemption control, relocation hiding, cacheline/page alignment macros, sparse `__percpu` typing, and arch implementations of scalar operations. It is foundational for scheduler, counters, refcounts, PMU state, and most SMP kernel code.

## Risks And Edge Cases
Risks include using `raw_cpu_*` without preemption/interrupt protection, unsupported scalar sizes, mismatched declaration/definition sections causing linkage errors, weak percpu symbol collisions, assuming `this_cpu_ptr()` is stable across preemption without protection, and architecture implementations missing required memory semantics.

## Test Signals
Build with SMP/UP, modules, debug preempt, sparse checking, and architectures with weak percpu definitions. Runtime tests should cover CPU hotplug, preemption debug warnings, per-CPU counter correctness under migration, and assembly/codegen sanity for 1/2/4/8-byte accessors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu-defs.h -->
