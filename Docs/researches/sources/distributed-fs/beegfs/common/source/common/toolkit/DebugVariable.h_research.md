<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/DebugVariable.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/DebugVariable.h

Purpose: Defines helper macros for environment-variable controlled debug tunables.

Important APIs/types: The file provides macro support used by code such as `MessagingTk` to override values from environment variables during debugging.

Control flow/state/persistence: Values are read from process environment at runtime where the macro is invoked. No persistent state is stored by the header itself.

Dependencies/integration: Integrated into diagnostics and test knobs for timing, networking, and other runtime behavior.

Risks/test signals: Environment overrides can change behavior unexpectedly in production-like tests. Tests should validate default use, override parsing, invalid values, and scope of the generated variable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/DebugVariable.h -->
