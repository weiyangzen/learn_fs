# sources/distributed-fs/ceph-client/tools/include/asm-generic/hugetlb_encode.h

## Purpose

This header defines the generic huge-page size encoding used in syscall flag fields that request hugetlb pages.

## APIs, State, and Dependencies

It defines `HUGETLB_FLAG_ENCODE_SHIFT`, `HUGETLB_FLAG_ENCODE_MASK`, and constants for sizes from 16 KiB through 16 GiB, each encoding `log2(size)` into bits 26 through 31. It has no includes, state, or control flow.

## Risks and Test Signals

The constants are ABI-facing. Incorrect shifts or log2 values would make mmap or other hugetlb flag users request the wrong size. Tests are compile checks and comparisons against UAPI/kernel definitions for `MAP_HUGE_*` style flags.
