# sources/distributed-fs/ceph-client/arch/x86/include/asm/percpu.h

Purpose: implements x86-specific per-CPU access primitives using segment-relative addressing (`gs` on x86-64, `fs` on x86-32), optimized inline assembly operations, early per-CPU storage, and size-specialized raw/this-CPU APIs.

Important APIs, types, and functions: defines `__percpu_seg`, `PER_CPU_VAR()`, `__my_cpu_offset`, `arch_raw_cpu_ptr()`, per-CPU type/register/op macros, raw and this CPU read/write/add/and/or/xchg/add_return/cmpxchg/try_cmpxchg variants for 1/2/4/8 bytes, 64-bit and 128-bit cmpxchg helpers where supported, `this_cpu_read_stable()`, bit-test helpers, `DECLARE_PER_CPU_CACHE_HOT(unsigned long, this_cpu_off)`, and `DEFINE/DECLARE/EXPORT_EARLY_PER_CPU*` macros.

Control flow: compile-time configuration selects assembler versus C, SMP versus UP, named address-space support versus explicit segment prefixes, and 32-bit versus 64-bit atomic widths. Operations expand to single x86 instructions where possible, often without LOCK because the target is CPU-local. Early per-CPU macros use temporary arrays before real per-CPU areas exist.

State and persistence: per-CPU variables are runtime kernel state. Early maps live in init data and hand off to normal per-CPU areas. No external persistence exists.

Dependencies and integration points: depends on generic per-CPU infrastructure, x86 segment setup, CPU feature alternatives for CMPXCHG8B/16B, `this_cpu_off`, and many scheduler/MM/IRQ fast paths.

Risks: segment prefix, address-space annotations, and inline-asm constraints are fragile. `raw_cpu_*` assumes CPU-local access without preemption/IRQ safety. 32-bit VDSO and 64-bit kernel combinations have special restrictions. Using XCHG would impose expensive lock semantics, so cmpxchg loops are deliberate.

Test signals: per-CPU selftests, SMP and UP builds, KCSAN/lockdep with raw versus this-CPU use, preemption stress, early boot CPU bring-up, 32-bit builds without CX8, x86-64 CX16 paths, and objdump inspection for expected segment-relative instructions.
