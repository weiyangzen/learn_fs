# sources/compression/lz4/programs/timefn.h

Purpose: declares the LZ4 program timing API.

Important APIs/types: `Duration_ns`, `TIME_t`, `TIME_INITIALIZER`, `TIME_getTime()`, `TIME_waitForNextTick()`, `TIME_support_MT_measurements()`, `TIME_span_ns()`, and `TIME_clockSpan_ns()`.

Control flow/state contract: callers compare two `TIME_t` measurements; absolute values are intentionally meaningless.

Dependencies/integration: implemented by `timefn.c`, consumed by `lz4io.c` and benchmark/progress code; C++ compatible.

Risks: unsigned subtraction assumes practical no-wrap intervals; multi-thread measurement quality depends on selected backend.

Test signals: exercised through progress/timing output in CLI and benchmark tests.
