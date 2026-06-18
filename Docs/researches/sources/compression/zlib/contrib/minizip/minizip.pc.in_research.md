# sources/compression/zlib/contrib/minizip/minizip.pc.in

## Purpose
This is the pkg-config template installed for the MiniZip library. It advertises include and linker flags for consumers that discover MiniZip with `pkg-config`.

## Important APIs, Types, and Functions
There are no executable APIs. The template defines `prefix`, `exec_prefix`, `libdir`, and `includedir`, then exposes package metadata: `Name: minizip`, description, version placeholder `@PACKAGE_VERSION@`, zlib license, `Libs: -L${libdir} -lminizip`, private zlib dependency `Libs.private: -lz`, and include flags.

## Control Flow
Build configuration substitutes the `@...@` placeholders, then installs the resulting `.pc` file. pkg-config consumers read the static fields to produce compiler and linker arguments.

## State and Persistence
The generated file is persisted into the install tree. It contains no mutable runtime state.

## Dependencies and Integration Points
Integrates MiniZip with pkg-config based build systems. It assumes the installed library is named `minizip` and that zlib is needed for static/private linkage.

## Risks and Edge Cases
`Requires:` is empty, so consumers relying only on public `Requires` may not see zlib unless they ask for static/private flags. The template does not expose optional bzip2 support. If install layout or library naming changes, this file must be updated with the CMake install/export logic.

## Test Signals
CMake package tests in the same tree exercise CMake config discovery, not this pkg-config template directly. A useful signal would be a post-install `pkg-config --cflags --libs minizip` check in packaging CI.
