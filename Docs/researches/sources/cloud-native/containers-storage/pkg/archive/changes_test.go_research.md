<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/changes_test.go

Purpose: broad behavioral tests for change detection, export/apply round-trips, and change size accounting.

Important APIs/types/functions: helpers `copyDir`, `FileType`, `FileData`, `createSampleDir`, `mutateSampleDir`, and `checkChanges`; tests `TestChangeString`, `TestChangesWithNoChanges`, `TestChangesWithChanges`, `TestChangesWithChangesGH13590`, `TestChangesDirsEmpty`, `TestChangesDirsMutated`, `TestApplyLayer`, and `TestChangesSize*`.

Control flow: tests create deterministic sample directories containing files, directories, symlinks, permissions, and timestamps. Mutation tests remove, replace, touch, and add entries, then compare expected `Change` sets. `TestApplyLayer` exports changes from a mutated tree, applies them back to the original, and asserts no remaining differences.

State/persistence: temporary filesystem state only. The tests force timestamps on non-symlinks and reset symlink times through platform hooks so symlink target changes are detectable.

Dependencies/integration: exercises `Changes`, `ChangesDirs`, `ExportChanges`, `ApplyLayer`, `NewTempArchive`, `ChangesSize`, `idtools.IDMappings`, and `system.Chtimes`.

Risks/test signal: tests guard subtle semantics: whiteout deletes, directory modification propagation, symlink target changes with same size/times, hardlink size accounting, and no-op diffs. Windows and Solaris skips highlight portability gaps.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_test.go -->
