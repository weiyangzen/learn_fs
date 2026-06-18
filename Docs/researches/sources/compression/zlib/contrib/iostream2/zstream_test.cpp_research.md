# sources/compression/zlib/contrib/iostream2/zstream_test.cpp

Purpose: demonstrates the `iostream2/zstream.h` wrapper for binary string records and formatted text output.

Important APIs/types/functions: `main`, `ozstream out`, `izstream in`, `read_string`, overloaded `operator<`, overloaded `operator>`, and formatted `operator<<` with `setw`, `setfill`, and `setprecision`.

Control flow: writes three strings to `temp.gz`, closes, reopens for input, reads the strings back into heap/stack buffers, prints them, reopens output, writes formatted text and a high-precision floating value, then deletes heap strings.

State and persistence: creates and overwrites `temp.gz` in the current directory. Allocates `x` through `read_string` and `y` manually.

Dependencies/integration: includes `zstream.h`, old math/stdlib/iomanip headers, and `cout`.

Risks: `void main()` is non-standard. The test is manual and has no assertions. It leaks no final `out.close()` before exit except destructor cleanup, and does not delete `z` because it is stack storage. It assumes old iostream headers.

Test signals: visible stdout should echo the three strings, and `zcat temp.gz` should show formatted text after the second phase.
