# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/flags.mk

## Purpose
Common compiler/linker flags for PowerPC selftests.

## Important APIs, Types, and Functions
Sets `GIT_VERSION`, appends include paths for `../include` and local `include`, enables warnings/debug/`-DGIT_VERSION`, and adds `-no-pie` linker mode.

## Control Flow
No control flow; included by child Makefiles before compilation.

## State and Persistence
No runtime state. Build commands inherit the variables.

## Dependencies and Integration Points
Integrates shared headers and version metadata across PowerPC selftests.

## Risks and Test Signals
Risk is compiler support for `-no-pie` or warning flags. Build output confirms compatibility.
