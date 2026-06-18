# File Research: sources/block-storage/mdadm/xmalloc.c

## Purpose
Fail-fast allocation wrappers for mdadm.

## Main Responsibilities
- Provides `xmalloc`, `xrealloc`, `xcalloc`, `xstrdup`, and `xmemalign`.
- On allocation failure, prints a message and exits with `MDADM_STATUS_MEM_FAIL`.

## Integration
Used throughout mdadm where allocation failure is considered fatal and callers should not manually propagate `ENOMEM`.

## Risks and Edge Cases
- These helpers terminate the process rather than returning errors, so they are unsuitable for code paths requiring cleanup/recovery on allocation failure.
