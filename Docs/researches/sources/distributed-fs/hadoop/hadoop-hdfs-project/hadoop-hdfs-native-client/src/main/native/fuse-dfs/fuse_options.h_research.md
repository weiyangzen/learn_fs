# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_options.h

## Purpose
Defines the global option structure and parser API for `fuse_dfs`.

## Important APIs, Types, And Functions
`struct options` stores protected paths, NameNode URI/port, debug/read-only/initchecks/no-permissions/trash/cache/private/read-buffer/direct-io/max-background fields. It declares global `options`, `dfs_opts`, `print_options`, `print_usage`, and `dfs_options`.

## Control Flow
No executable flow in the header; parser implementation fills the global struct before mount initialization.

## State, Persistence, And Dependencies
The global `options` variable is defined in this header, so every translation unit including it risks a tentative definition under old C behavior. The top-level CMake uses `-fcommon` on GCC >= 10 to preserve this pattern.

## Integration Points
Included by startup, init, and option parsing code.

## Risks
Defining storage in a header is fragile and non-idiomatic. Fields have mixed ownership: some strings point to argv/storage, others are heap-allocated.

## Test Signals
Build/link success depends on compiler common-symbol behavior; runtime option tests validate field propagation.
