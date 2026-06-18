# sources/distributed-fs/ceph-client/arch/x86/mm/Makefile

## Purpose
Defines the build composition and instrumentation policy for `arch/x86/mm`.

## Important APIs, Types, And Functions
This is a kbuild file, not C code. It controls object lists such as `init.o`, `fault.o`, `ioremap.o`, `extable.o`, `tlb.o`, `cpu_entry_area.o`, and conditional objects for huge pages, page-table dumps, KASAN/KMSAN, MMIOTRACE, NUMA, pkeys, KASLR, PTI, and memory encryption.

## Control Flow
Kbuild evaluates configuration symbols to choose object files and sanitizer/tracing flags. Several files disable KCOV/KASAN/KMSAN/KCSAN or `-pg` instrumentation because they run in boot, entry, memory-encryption, or sensitive page-table contexts.

## State And Persistence
No runtime state. It persists build policy in the source tree.

## Dependencies And Integration Points
Integrates `arch/x86/mm` with kernel configuration options and compiler instrumentation. Conditional object selection must match symbol definitions and source availability.

## Risks
Incorrect instrumentation can recurse in entry/page-table code or break boot. Missing conditional objects silently remove features; wrong sanitizer exclusions can produce false positives or runtime faults.

## Test Signals
Build matrix across 32/64-bit, KASAN/KMSAN/KCSAN/KCOV, PTDUMP/debugfs, hugetlb, NUMA backends, MMIOTRACE, PTI, KASLR, pkeys, and AMD memory encryption.
