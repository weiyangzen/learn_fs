# sources/distributed-fs/orangefs/src/common/events/fmt_fsm.h

Purpose: Declares the `ff_format` and nested `ff_pattern` C++ classes used to parse and encode TAU event format descriptors.

Important APIs/types: `ff_pattern` stores the textual pattern, length modifier count, stored size, unsigned flag, parser state, error/end flags, and type. `ff_format` stores raw/parsed formats, an array of 16 patterns, pattern count, total size, and initialization flag. Template `promoteIntegral()` helpers decode stored bytes into caller-requested integral types.

Control flow contract: Call `init()` with a format string, `parse()` to populate patterns, `suck()` to encode varargs, `bfprint()` to print stored bytes, and `promoteIntegral()` to extract one integral pattern.

State/persistence: Objects hold parsed metadata and are copied into event definition structures. No external persistence.

Dependencies/integration: Includes C/C++ standard headers and is consumed by TAU event files that are compiled as C++.

Risks: Constructors accept non-const `char *`, limiting use with string literals under stricter C++ compilers. Fixed arrays and `strncpy()` may truncate silently. Template decoding assumes stored byte layout and endian match the writing process.

Test signals: Compile under the repository's C++ mode, exercise copy construction/assignment through event bundle refresh, and validate `promoteIntegral()` for signed/unsigned width variants.
