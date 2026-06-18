# sources/distributed-fs/ceph-client/kernel/sched/rq-offsets.c

## Purpose
Generates build-time offsets for fields in `struct rq` needed by low-level or architecture code. This file is compiled as a small kbuild helper rather than linked into normal scheduler runtime.

## APIs, Control Flow, and State
The file defines `COMPILE_OFFSETS`, includes kbuild offset helpers and `sched.h`, and has a single `main()` that emits `DEFINE(RQ_nr_pinned, offsetof(struct rq, nr_pinned));`. There is no runtime kernel control flow and no persistent runtime state. The only output is a generated constant representing the offset of `rq.nr_pinned`.

## Dependencies and Integration Points
Depends on `linux/kbuild.h`, `linux/types.h`, `offsetof`, and the exact layout of `struct rq` in `sched.h`. It integrates with the kernel build's generated-offset mechanism and any low-level code or tooling that consumes `RQ_nr_pinned`.

## Risks and Test Signals
Risks are build failures or silent ABI/layout mismatches if `struct rq` changes and consumers are not updated. Since the helper has no runtime behavior, signals are compile success, generated-offset diffs, allmodconfig/architecture builds that use the offset, and tests for features that consume `rq->nr_pinned` through generated assembly constants.
