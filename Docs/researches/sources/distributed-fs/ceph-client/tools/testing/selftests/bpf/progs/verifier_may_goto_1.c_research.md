# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_may_goto_1.c

## Purpose
This file tests verifier and translator handling of raw `may_goto` (`BPF_JMP | BPF_JCOND`) instructions with zero and positive offsets.

## Important APIs, Types, And Functions
It uses raw tracepoint sections, architecture filters for x86_64/s390x/arm64, `__xlated` expectations, and `BPF_RAW_INSN(BPF_JMP | BPF_JCOND, ...)` emitted through `__imm_insn`.

## Control Flow
`may_goto_simple` and `may_goto_batch_0` emit one or more zero-offset conditional jumps that translate down to `r0 = 1; exit`. `may_goto_batch_1` uses offsets 2/1/0 in a batch, and `may_goto_batch_2` checks the expanded translation with internal counter stack slots before normal exit.

## State And Persistence
There is no runtime persistence. Verifier state includes may-goto expansion/accounting, branch reachability, generated counter stack slots, and architecture-specific translated output.

## Dependencies And Integration Points
It integrates with core verifier control-flow validation for newer BPF ISA behavior. The selftest harness checks both accepted and rejected variants.

## Risks
If may-goto is treated as an ordinary jump, valid bounded constructs may fail. If treated too permissively, non-terminating or unsafe paths may be accepted.

## Test Signals
Signals are `__success` plus exact translated instruction snippets, including compact translations for zero-offset batches and the longer counter-based expansion for offset 2/0.
