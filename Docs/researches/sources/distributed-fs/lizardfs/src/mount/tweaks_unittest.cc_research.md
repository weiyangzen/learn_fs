## sources/distributed-fs/lizardfs/src/mount/tweaks_unittest.cc

Purpose: GoogleTest coverage for `Tweaks`.

Important tests: `GetAllValues` registers uint32, uint64, and bool atomics and verifies tab/newline formatting and boolalpha output. `SetValue` verifies invalid strings leave values unchanged, numeric parsing accepts whitespace/prefix numeric data, uint64 updates independently, and bool values parse `true`, `false`, and `true\n`.

Dependencies and integration: isolated unit test depending only on gtest and `tweaks.h`.

Risks and gaps: does not cover duplicate names, unknown names, concurrent access, registry lifetime after referenced atomics go out of scope, or negative/out-of-range numeric parsing.
