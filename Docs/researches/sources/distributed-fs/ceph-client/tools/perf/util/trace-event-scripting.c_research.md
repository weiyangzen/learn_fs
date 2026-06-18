# sources/distributed-fs/ceph-client/tools/perf/util/trace-event-scripting.c

## Purpose

`trace-event-scripting.c` manages scripting-engine registration and common scripting context updates, and it formats branch/sample flags for script output.

## Important APIs, Types, and Functions

Public globals/functions include `scripting_max_stack`, `scripting_context`, `script_spec__lookup()`, `script_spec__for_each()`, `setup_python_scripting()`, `setup_perl_scripting()`, `scripting_context__update()`, and `perf_sample__sprintf_flags()`. Internal `struct script_spec` links a spec string such as `Python`, `py`, `Perl`, or `pl` to `struct scripting_ops`. Unsupported Python/Perl ops print rebuild guidance and return errors for start/generate.

## Control Flow and State

Setup allocates the global scripting context and registers language aliases to either real ops or unsupported stubs based on build flags. Context update copies the current event, sample, evsel, address locations, raw data, and trace-event parser handle into the global context. Flag formatting first tries named branch types and events, including trace begin/end and transaction/additional-state annotations; if no named format matches, it falls back to raw bit characters.

## Dependencies and Integration Points

It depends on libtraceevent when available, perf samples, evsels, address locations, and optional Python/Perl support. It is used by `perf script` and generated scripts.

## State and Persistence Behavior

Script specs and scripting context are process-global. Registered ops persist for the process lifetime. Context fields are overwritten for each processed event.

## Risks and Test Signals

Risks include duplicate spec registration disabling scripting, missing context allocation, unsupported builds returning confusing errors, and flag string truncation/alignment mistakes. Tests should verify Python/Perl alias lookup, unsupported messages, context update for tracepoint and non-tracepoint evsels, callback iteration, and formatting for calls, returns, trace boundaries, branch misses, not-taken branches, transactions, and unknown bits.
