# sources/distributed-fs/ceph-client/fs/tests/exec_kunit.c

## Purpose
This KUnit suite validates `bprm_stack_limits()`, which computes exec argument/environment stack limits and rejects unsafe counts.

## Important APIs, Types, and Functions
The test defines `struct bprm_stack_limits_result`, a table of `linux_binprm` input cases, `exec_test_bprm_stack_limits()`, and suite metadata named `"exec"`. It checks constants `_STK_LIM`, `ARG_MAX`, and `MAX_ARG_STRINGS`, then validates return codes and, under `CONFIG_MMU`, calculated `bprm.argmin`.

## Control Flow and State
Inputs cover negative `argc`/`envc`, maximum string counts, overflow-prone pointer count combinations, pathological `bprm->p`, zero stack rlimit raised to `ARG_MAX`, exact pointer capacity boundaries, and the `_STK_LIM` three-quarter cap. Each table row copies the `linux_binprm`, calls `bprm_stack_limits()`, and compares result/error fields.

## Persistence, Dependencies, and Integration
This is test-only code depending on KUnit and exec internals. It has no persistent state; it exercises pure limit calculation over stack pointer and rlimit fields.

## Risks and Test Signals
The suite targets security-sensitive overflow and bounds risks in exec argument setup, especially 32-bit arithmetic bypasses and off-by-one pointer reservations. Passing tests signal that invalid counts produce `-E2BIG` and valid boundary cases compute expected `argmin`.
