# sources/distributed-fs/lizardfs/src/metadump/CMakeLists.txt

## Purpose

`src/metadump/CMakeLists.txt` builds and installs the `mfsmetadump` executable. The source was read as a complete 6-line CMake file.

## Important APIs, Types, and Functions

It adds the current source directory to include paths, collects all local sources into `METADUMP_SOURCES`, creates `mfsmetadump`, leaves `target_link_libraries` empty, and installs the binary into `${SBIN_SUBDIR}`.

## Control Flow

CMake configure/generate flow discovers sources with `aux_source_directory`, then build flow compiles the executable.

## State and Persistence Behavior

No runtime persistence. Build output is the installed `mfsmetadump` utility.

## Dependencies and Integration Points

It integrates the standalone metadata dump reader with the project install layout. The empty link line implies `mfsmetadump.cc` is intended to compile with only common headers or inherited build defaults.

## Risks and Edge Cases

`aux_source_directory` can accidentally pick up new local files. Empty linking may break if the implementation starts requiring common library objects beyond header-only helpers/macros.

## Test Signals

Build `mfsmetadump`, run install packaging checks, and execute the binary on fixture metadata files.
