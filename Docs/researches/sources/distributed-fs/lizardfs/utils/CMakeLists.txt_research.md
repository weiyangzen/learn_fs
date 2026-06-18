<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/utils/CMakeLists.txt

Purpose: declares build and install rules for LizardFS test/support utilities and LD_PRELOAD libraries used by the integration suite.

Important APIs, functions, and commands: defines `add_executable`, `add_library`, `endif`, `if`, `include_directories`, `install`, `target_link_libraries`; uses `file-generate`, `file-overwrite`, `file-validate`, `file-validate-growing`, `posixlockcmd`, `flockcmd`.

Control flow: Control flow is CMake configure-time declaration: optional compiler flags are applied, libraries/executables are declared, linked where needed, and installed into the configured binary or library subdirectories.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: CMake build graph, LizardFS CLI/test helpers.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked; EIO injection depends on chunk-file naming and disk health classification. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/utils/CMakeLists.txt -->
