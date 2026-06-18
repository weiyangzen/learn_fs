# sources/distributed-fs/lizardfs/src/unittests/unittests.in

Purpose: Template shell launcher for unit tests.

Important APIs/types/functions: Shell variables and configured paths; execution of the generated unittest binary from the build/install context.

Control flow: The script template is configured by CMake and runs the relevant unittest executable with forwarded arguments/environment.

State and persistence: No persistent state beyond process exit code.

Dependencies and integration: Used by the build/test harness to invoke compiled tests consistently.

Risks and test signals: Correctness depends on CMake substitutions and executable paths. The file is small and has no direct C++ behavior.
