# sources/distributed-fs/ceph-client/tools/include/nolibc/math.h

## Purpose
Provides minimal floating absolute-value helpers for nolibc.

## APIs, Types, and Functions
Defines `fabs`, `fabsf`, and `fabsl` as inline sign checks returning the positive magnitude of double, float, and long double values.

## Control Flow, State, and Persistence
Control flow is a single comparison and conditional negation. No math library state, errno, floating exception handling, or NaN special handling beyond C comparison semantics is implemented.

## Dependencies and Integration
Depends only on the nolibc include surface. It integrates with small programs that need basic absolute value without linking libm.

## Risks and Test Signals
Risks are callers expecting full libm behavior, signed-zero preservation, NaN payload semantics, or errno/fenv side effects. Test signals are positive/negative values, zero, infinity, NaN behavior, and builds without libm.
