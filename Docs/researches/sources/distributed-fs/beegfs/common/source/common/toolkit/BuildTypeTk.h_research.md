<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/BuildTypeTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/BuildTypeTk.h

Purpose: Provides build-type detection and consistency checks.

Important APIs/types: `FhgfsBuildTypeDebug` enumerates debug, release, and unknown. `BuildTypeTk` exposes `getCommonLibDebugBuildType`, `getCurrentDebugBuildType`, and `checkDebugBuildTypes`.

Control flow/state/persistence: Header inline methods compare compile-time build type against the linked common library result. No persistence.

Dependencies/integration: Used to detect mixed debug/release component builds.

Risks/test signals: Check behavior depends on macros and link unit boundaries. Build tests should validate mixed-build detection where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/BuildTypeTk.h -->
