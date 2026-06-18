# sources/distributed-fs/ceph-client/mm/vma_exec.c

## Purpose

`vma_exec.c` contains VMA-only helpers used during `execve()` setup: creation of the temporary initial stack VMA at the architecture maximum stack address and relocation of that stack VMA downward once the final placement is known.

## Important APIs, Types, and Functions

- `create_init_stack_vma(struct mm_struct *mm, struct vm_area_struct **vmap, unsigned long *top_mem_p)` allocates and inserts the one-page initial stack VMA with `VM_STACK_FLAGS | VM_STACK_INCOMPLETE_SETUP`.
- `relocate_vma_down(struct vm_area_struct *vma, unsigned long shift)` expands a VMA to cover old and new stack ranges, moves page tables downward, frees old page-table ranges, and shrinks the VMA to the relocated range.
- The implementation uses `VMG_STATE`, `vma_expand()`, `PAGETABLE_MOVE`, `move_page_tables()`, `free_pgd_range()`, `mmu_gather`, and `vma_shrink()`.

## Control Flow

`create_init_stack_vma()` allocates a VMA, marks it anonymous, takes the mmap write lock killably, runs `ksm_execve()`, initializes a one-page stack at `[STACK_TOP_MAX - PAGE_SIZE, STACK_TOP_MAX)`, applies soft-dirty when supported, sets page protections, inserts it with `insert_vm_struct()`, initializes `mm->stack_vm` and `mm->total_vm`, unlocks, and returns the VMA plus the highest word-addressable stack location. Error paths unwind KSM, mmap lock, and the VMA allocation.

`relocate_vma_down()` computes old/new ranges, verifies no VMA exists between the new start and old VMA, expands the VMA to cover `[new_start, old_end)`, moves page tables with `for_stack = true`, frees the cleared old PGD range with different bounds for overlapping versus non-overlapping moves, then shrinks the VMA to `[new_start, new_end)`.

## State and Persistence

The functions mutate the target `mm_struct` and stack VMA: VMA range, pgoff, page tables, `mm->stack_vm`, `mm->total_vm`, KSM exec state, and maple-tree placement. Transient state includes `vma_iterator`, `vma_merge_struct`, `mmu_gather`, and `pagetable_move_control`.

## Dependencies and Integration Points

This file depends on VMA allocation/insertion/expand/shrink from the VMA subsystem, KSM exec hooks, architecture stack limits, page-table movement/freeing, mmap locking, soft-dirty support, and exec code that later finalizes stack placement.

## Risks

- The relocation helper is explicitly specialized for early exec stack relocation; using it for general VMA moves would bypass many checks that `mremap()` or mmap paths perform.
- If `move_page_tables()` moves only a partial range, the function returns `-ENOMEM` and relies on process cleanup to remove the inconsistent intermediate state.
- The no-intervening-VMA check and range arithmetic must hold, or expansion can cover an unintended mapping.
- Error unwinding in initial stack creation must keep KSM and mmap lock state balanced.

## Test Signals

Signals include execve tests across stack-randomization paths, failure injection for `vm_area_alloc()`, `mmap_write_lock_killable()`, `ksm_execve()`, `insert_vm_struct()`, and `move_page_tables()`, plus debug VM/maple-tree validation after stack relocation.
