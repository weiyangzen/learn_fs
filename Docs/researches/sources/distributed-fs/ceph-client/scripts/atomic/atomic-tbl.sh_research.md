# sources/distributed-fs/ceph-client/scripts/atomic/atomic-tbl.sh

## Purpose
`atomic-tbl.sh` is a shared shell library for scripts that generate Linux atomic operation headers from `atomics.tbl`.

## APIs, Types, And Functions
It provides metadata predicates (`meta_has_ret`, acquire/release/relaxed checks, implicit relaxed checks), template discovery (`find_template`, `find_fallback_template`, `find_kerneldoc_template`), type/argument helpers (`gen_ret_type`, `gen_param_type`, `gen_params`, `gen_args`), kerneldoc generation, and prototype variant expansion (`gen_proto*`).

## Control Flow
Generator scripts source this file, then feed table rows into `gen_proto()`. The metadata string expands into fetch, return, acquire, release, relaxed, and full-order variants; concrete `gen_proto_order_variant()` is supplied by each generator.

## State And Persistence
It uses shell locals and environment variable `ATOMICDIR`. It writes generated text to stdout through caller-provided functions but persists nothing itself.

## Dependencies And Integration Points
It depends on POSIX shell and sourced templates under `scripts/atomic/fallbacks` and `kerneldoc`. It integrates all atomic header generators around a common metadata vocabulary.

## Risks And Test Signals
Risks include shell word-splitting in table arguments, missing templates, and mismatched metadata semantics. Test signals are regenerated atomic headers matching checked-in output and complete variants for every `atomics.tbl` row.
