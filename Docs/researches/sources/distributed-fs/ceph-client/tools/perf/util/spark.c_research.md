# sources/distributed-fs/ceph-client/tools/perf/util/spark.c

## Purpose

`spark.c` renders a compact Unicode sparkline for a vector of unsigned long values. It is a small presentation helper for perf output that wants trend visualization without graphics.

## Important APIs, Types, and Functions

The only exported function is `print_spark(char *bf, int size, unsigned long *val, int numval)`. It uses the eight glyphs defined by `NUM_SPARKS` in `spark.h` and `SPARK_SHIFT` fixed-point scaling.

## Control Flow and Data Flow

The function scans all values to find `min` and `max`, computes a fixed-point step `f = ((max - min) << SPARK_SHIFT) / (NUM_SPARKS - 1)`, clamps `f` to at least one, then appends one tick glyph per value using `scnprintf()`. The glyph index is `((val[i] - min) << SPARK_SHIFT) / f`.

## State and Persistence Behavior

There is no persistent or global state other than the static tick table. Output is written into the caller-provided buffer and the function returns the number of bytes printed.

## Dependencies and Integration Points

It depends on Linux `scnprintf()` and `<limits.h>`. Callers must provide an adequately sized buffer and accept UTF-8 glyph output.

## Risks and Edge Cases

The implementation assumes `numval > 0`; an empty vector leaves `min` and `max` at sentinel values and can underflow. Very small buffers rely on `scnprintf()` truncation behavior. Since each glyph is multi-byte UTF-8, byte count and display column count differ.

## Test Signals

Tests should cover constant arrays, increasing/decreasing arrays, mixed ranges, small output buffers, and Unicode rendering in terminal output. A defensive caller test should avoid invoking it with zero values.
