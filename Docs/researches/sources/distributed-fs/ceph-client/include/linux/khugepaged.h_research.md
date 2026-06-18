# sources/distributed-fs/ceph-client/include/linux/khugepaged.h

## Purpose

`khugepaged.h` declares the khugepaged transparent hugepage scanning interface. It lets memory-management paths start/stop khugepaged, enroll or remove address spaces and VMAs, update memory thresholds, and collapse PTE-mapped THPs. The source was read as a complete 60-line file.

## Important APIs, Types, and Functions

Important declarations under `CONFIG_TRANSPARENT_HUGEPAGE` include `khugepaged_attr_group`, `khugepaged_init()`, `khugepaged_destroy()`, `start_stop_khugepaged()`, `__khugepaged_enter()`, `__khugepaged_exit()`, `khugepaged_enter_vma()`, `khugepaged_min_free_kbytes_update()`, `current_is_khugepaged()`, and `collapse_pte_mapped_thp()`. Inline helpers are `khugepaged_fork()` and `khugepaged_exit()`. `khugepaged_max_ptes_none` is always declared.

## Control Flow

Process memory setup and VMA changes call enter helpers when hugepage flags are set. Fork inherits eligibility through `khugepaged_fork()`, and mm teardown calls exit. The khugepaged thread scans eligible ranges and may collapse mappings.

## State and Persistence Behavior

State lives in `mm_struct` flags, VMA flags, khugepaged sysfs tunables, and the khugepaged worker thread. No persistent storage exists.

## Dependencies and Integration Points

It integrates with THP, sysfs attribute groups, mm lifecycle, fork/exit, VMA policy, and PTE/PMD collapse paths.

## Risks and Edge Cases

Disabled THP builds stub out most behavior. Fork enrollment is best-effort and depends on `MMF_VM_HUGEPAGE`. Collapse paths must handle races with page faults, unmaps, and memory pressure.

## Test Signals

THP selftests, khugepaged sysfs toggling, fork/exit enrollment tests, collapse of PTE-mapped THP, and `CONFIG_TRANSPARENT_HUGEPAGE=n` build coverage are useful.
