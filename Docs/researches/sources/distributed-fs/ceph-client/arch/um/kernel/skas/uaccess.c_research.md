# sources/distributed-fs/ceph-client/arch/um/kernel/skas/uaccess.c

## Purpose
Implements UML SKAS user-memory access primitives and futex atomics by walking guest page tables, faulting pages in as needed, and temporarily mapping the backing host page into kernel address space.

## Important APIs, Types, and Functions
`virt_to_pte()` resolves a user virtual address to a PTE. `maybe_map()` invokes `handle_page_fault()` if the PTE is absent or not writable. `buffer_op()` runs page-split operations. Exports `raw_copy_from_user()`, `raw_copy_to_user()`, `strncpy_from_user()`, `__clear_user()`, `strnlen_user()`, `arch_futex_atomic_op_inuser()`, and `futex_atomic_cmpxchg_inatomic()`.

## Control Flow, State, and Persistence
State is transient: current mm page tables, highmem mappings on 32-bit, preemption/pagefault-disable windows, and returned remaining-byte counts. Faults may update page tables and TLB sync state through the normal page-fault path.

## Dependencies and Integration Points
Depends on `handle_page_fault()` from `trap.c`, page-table helpers, highmem APIs, futex operation definitions, and exported uaccess ABI expected by generic kernel code.

## Risks and Test Signals
Risks include partial-copy accounting, missing access checks, highmem kmap misuse, non-atomic futex behavior under contention, and pagefault-disabled interactions. Test copy_to/from_user boundary crossings, unmapped userspace pointers, futex operations, 32-bit highmem, and fault injection.
