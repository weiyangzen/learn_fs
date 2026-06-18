# sources/distributed-fs/ceph-client/fs/ocfs2/mmap.h

## Purpose
`mmap.h` declares the OCFS2 mmap preparation hook.

## Important APIs, types, and functions
It exposes `ocfs2_mmap_prepare(struct vm_area_desc *desc)`, which installs OCFS2 VM operations for file mappings.

## Control flow
The file operation mmap path calls this helper with a `vm_area_desc`; implementation code assigns `.fault` and `.page_mkwrite` handlers.

## State and persistence behavior
The header has no state. The declared function affects VMA runtime operations and can trigger atime locking in its implementation.

## Dependencies and integration points
It integrates OCFS2 file operations with Linux VMA setup. Including files must provide `struct vm_area_desc`.

## Risks and edge cases
The main risk is build/API drift with the kernel mmap prepare signature. Runtime mmap risks live in `mmap.c`.

## Test signals
Build coverage should exercise mmap operation wiring. Runtime tests should verify VM operations are installed and mmap write faults use OCFS2 locking.
