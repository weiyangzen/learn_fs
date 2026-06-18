<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-byteswap.h -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi-byteswap.h

Purpose: Defines byte-swap helpers and BMI host/network encoding macros used by BMI wire-format code. The BMI encoding is little-endian on little-endian hosts and swapped on big-endian hosts, preserving the historic PVFS/BMI on-wire convention.

Important APIs, types, and functions: Exposes `__bswap_16`, `__bswap_32`, `__bswap_64` where not already defined, plus `htobmi16/32/64` and `bmitoh16/32/64`. GNU C builds use statement-expression macros for efficient constant and variable swaps; non-GNU builds receive inline functions for 16/32-bit only.

Control flow and state: Header-only arithmetic macros/functions; no runtime state or persistence. The 64-bit GNU path uses a union to split and swap halves unless the value is compile-time constant.

Dependencies and integration points: Includes `pvfs2-internal.h` and relies on `WORDS_BIGENDIAN` to choose conversion direction. BMI methods and protocol encoders should use these macros for fields carried over the network.

Risks and test signals: Non-GNU big-endian builds hit a deliberate 64-bit unsupported error. Macro arguments for host/BMI conversion are not parenthesized in the little-endian identity definitions, so expression use should be checked. Tests should round-trip 16/32/64-bit values on simulated endian configurations and compile non-GNU Windows paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-byteswap.h -->
