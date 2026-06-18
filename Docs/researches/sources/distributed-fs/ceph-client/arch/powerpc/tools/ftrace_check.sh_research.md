# sources/distributed-fs/ceph-client/arch/powerpc/tools/ftrace_check.sh

## Purpose
`ftrace_check.sh` verifies that the built kernel places `ftrace_caller` and `ftrace_tramp_text` within branch reach constraints required by PowerPC ftrace.

## Important APIs, Types, And Functions
The script consumes paths to `nm` and `vmlinux`, extracts `_stext`, `ftrace_caller`, and `ftrace_tramp_text` addresses, computes offsets with `bc`, and compares them against 32 MiB and 64 MiB limits.

## Control Flow
After argument validation, it reads symbol addresses, normalizes them to uppercase hex, computes `ftrace_caller - _stext` and `ftrace_tramp_text - ftrace_caller`, then emits explicit errors and exits nonzero when either architectural reachability limit is exceeded.

## State And Persistence
It is stateless and writes no files.

## Dependencies And Integration Points
It depends on bash, `nm`, `grep`, `cut`, `tr`, `bc`, and final `vmlinux` symbols. It is a post-link architecture validation gate for function tracing.

## Risks
Missing symbols produce empty arithmetic inputs and confusing failures. Symbol type assumptions must match linker output. The check is address-distance based and does not inspect individual call sites, so it complements but does not replace runtime ftrace testing.

## Test Signals
A passing run exits zero. Failure messages identify whether `ftrace_caller` is too far from `_stext` or kernel text extends too far from `ftrace_caller`.
