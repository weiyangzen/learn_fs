# sources/distributed-fs/ceph-client/tools/include/linux/align.h

## Purpose

This header exposes kernel-style alignment macros to tools code.

## APIs, State, and Dependencies

It includes `<uapi/linux/const.h>` and defines `ALIGN`, `ALIGN_DOWN`, and `IS_ALIGNED`. These macros operate on caller-provided values and have no state.

## Risks and Test Signals

Alignment arguments are expected to be powers of two. Misuse with side-effect expressions can evaluate arguments more than once depending on nested macros. Tests should compile users and validate representative align-up, align-down, and aligned checks for integer and pointer-sized values.
