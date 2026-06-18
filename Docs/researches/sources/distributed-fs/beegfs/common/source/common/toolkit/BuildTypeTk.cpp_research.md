<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/BuildTypeTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/BuildTypeTk.cpp

Purpose: Returns the debug/release build type for the common library.

Important APIs/functions: `BuildTypeTk::getCommonLibDebugBuildType` returns debug or release based on compile-time macros.

Control flow/state/persistence: Compile-time conditional logic only, no runtime state.

Dependencies/integration: Used with `BuildTypeTk.h` to check build-type consistency across components.

Risks/test signals: Tests/build checks should confirm debug builds report debug and release builds report release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/BuildTypeTk.cpp -->
