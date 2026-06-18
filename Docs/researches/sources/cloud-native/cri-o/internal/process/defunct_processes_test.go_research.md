# sources/cloud-native/cri-o/internal/process/defunct_processes_test.go

Purpose: validates zombie-process counting against procfs fixture directories.

Important APIs/types/functions: tests `process.DefunctProcessesForPath`.

Control flow: success contexts call the function with fixture roots containing zombie states, no zombies, no process directories, or no directories. Failure contexts call it with a missing path and a regular file path.

State and persistence behavior: read-only use of checked-in test fixture files.

Dependencies and integration points: uses Ginkgo/Gomega assertions and the public process API.

Risks: exact error-string assertions are OS/runtime-sensitive for path formatting. Fixture-relative paths require the package test working directory.

Test signals: expected counts are 7 zombies for `proc_success_1` and 0 for the other success fixtures; invalid path and non-directory cases return count 0 plus errors.
