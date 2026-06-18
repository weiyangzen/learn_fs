# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Sizes.java

## Purpose

`Sizes.java` is a constants holder for common binary byte sizes. It avoids repeated magic numbers for powers of two and selected MiB multiples.

## Important APIs, types, and functions

- `Sizes` is `final` and contains only public static final integer constants.
- Constants run from `S_0`, `S_256`, `S_512`, `S_1K` through `S_32M`, plus `S_5M` and `S_10M`.
- Larger constants are built by left-shifting the previous constant, preserving compile-time constant behavior.

## Control flow

There is no executable control flow beyond class initialization of constants.

## State and persistence behavior

There is no mutable state and no serialization. Constants are inlined by Java compilers where used.

## Dependencies and integration points

The class only depends on Hadoop classification annotations. It is a small public evolving utility for IO and configuration code that needs readable byte-size constants.

## Risks and edge cases

- Javadoc comments for `S_2K`, `S_4K`, `S_8M`, `S_16M`, and `S_32M` contain wording mistakes about KiB/MiB labels, though the numeric constants are correct.
- Values are `int`; this file intentionally stops far below integer overflow.

## Test signals

Compile-time or unit checks can assert key values such as `S_1K == 1024`, `S_1M == 1048576`, `S_5M == 5 * S_1M`, and `S_10M == 10 * S_1M`.
