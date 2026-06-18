# subset-b-009213 research

Grouped research report for generated CrashMonkey seq1 C++ tests under `sources/test-tools/crashmonkey/code/tests/seq1`. Each section preserves the exact source path and is wrapped for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang270.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang270.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename A/foo to root bar, then create and fsync A/bar. This is one generated C++ test in the seq1 family, focused on the `rename/create/fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close A/foo; rename A/foo to bar; create A/bar; fsync A/bar; checkpoint; close A/bar. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: metadata rename across directories with later fsync of a different new file inside A. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang270.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang271.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang271.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename A/foo to root bar, then recreate and fsync A/foo. This is one generated C++ test in the seq1 family, focused on the `rename/recreate/fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close A/foo; rename A/foo to bar; recreate A/foo; fsync A/foo; checkpoint; close A/foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: source-name resurrection after rename with file-data durability on the recreated path. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang271.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang272.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang272.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename A/foo to root bar, then fsync the mount root directory. This is one generated C++ test in the seq1 family, focused on the `rename/root-dir-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close A/foo; rename A/foo to bar; open mount root as O_DIRECTORY; fsync root directory; checkpoint; close root fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: parent/root directory durability for a rename out of A. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang272.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang273.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang273.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename A/foo to root bar, then create and fsync root foo. This is one generated C++ test in the seq1 family, focused on the `rename/unrelated-file-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close A/foo; rename A/foo to bar; create foo; fsync foo; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: namespace interaction between a moved file and a separate root file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang273.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang274.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang274.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename A/foo to root bar, then global sync. This is one generated C++ test in the seq1 family, focused on the `rename/sync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close A/foo; rename A/foo to bar; CmSync; checkpoint. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: global flush coverage for a cross-directory rename. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang274.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang275.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang275.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename A/foo to A/bar, then fsync directory A. This is one generated C++ test in the seq1 family, focused on the `same-dir-rename/parent-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close A/foo; rename A/foo to A/bar; open A as O_DIRECTORY; fsync A; checkpoint; close A fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: same-directory rename durability through parent directory fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang275.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang276.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang276.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename A/foo to A/bar, then recreate and fsync A/foo. This is one generated C++ test in the seq1 family, focused on the `same-dir-rename/recreate-source` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close A/foo; rename A/foo to A/bar; recreate A/foo; fsync A/foo; checkpoint; close A/foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: same-directory rename followed by source-name recreation. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang276.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang277.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang277.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename A/foo to A/bar, then open and fsync A/bar. This is one generated C++ test in the seq1 family, focused on the `same-dir-rename/destination-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close A/foo; rename A/foo to A/bar; open A/bar; fsync A/bar; checkpoint; close A/bar. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: destination inode fsync after same-directory rename. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang277.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang278.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang278.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename A/foo to A/bar, then global sync. This is one generated C++ test in the seq1 family, focused on the `same-dir-rename/sync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close A/foo; rename A/foo to A/bar; CmSync; checkpoint. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: same-directory rename durability under sync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang278.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang279.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang279.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename root bar to A/bar, then fsync directory A. This is one generated C++ test in the seq1 family, focused on the `rename-into-dir/parent-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close bar; rename bar to A/bar; open A as O_DIRECTORY; fsync A; checkpoint; close A fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: rename into a directory with destination-parent fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang279.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang280.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang280.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename root bar to A/bar, then recreate and fsync root bar. This is one generated C++ test in the seq1 family, focused on the `rename-into-dir/recreate-source` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close bar; rename bar to A/bar; recreate bar; fsync bar; checkpoint; close bar. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: source-name recreation after moving a file into A. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang280.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang281.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang281.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename root bar to A/bar, then fsync A/bar. This is one generated C++ test in the seq1 family, focused on the `rename-into-dir/destination-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close bar; rename bar to A/bar; open A/bar; fsync A/bar; checkpoint; close A/bar. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: destination file fsync after rename into A. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang281.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang282.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang282.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename root bar to A/bar, then create and fsync A/foo. This is one generated C++ test in the seq1 family, focused on the `rename-into-dir/sibling-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close bar; rename bar to A/bar; create A/foo; fsync A/foo; checkpoint; close A/foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: rename into A plus separate sibling file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang282.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang283.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang283.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename root bar to A/bar, then fsync mount root. This is one generated C++ test in the seq1 family, focused on the `rename-into-dir/root-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close bar; rename bar to A/bar; open mount root as O_DIRECTORY; fsync root directory; checkpoint; close root fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: source-parent/root directory durability for rename into A. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang283.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang284.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang284.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename root bar to A/bar, then create and fsync root foo. This is one generated C++ test in the seq1 family, focused on the `rename-into-dir/unrelated-file-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close bar; rename bar to A/bar; create foo; fsync foo; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: rename into A plus unrelated root file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang284.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang285.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang285.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename root bar to A/bar, then global sync. This is one generated C++ test in the seq1 family, focused on the `rename-into-dir/sync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close bar; rename bar to A/bar; CmSync; checkpoint. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: rename into A with global flush. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang285.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang286.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang286.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename A/bar to root bar, then fsync directory A. This is one generated C++ test in the seq1 family, focused on the `rename-out/source-parent-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close A/bar; rename A/bar to bar; open A as O_DIRECTORY; fsync A; checkpoint; close A fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: rename out of A with source-parent fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang286.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang287.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang287.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename A/bar to root bar, then fsync root bar. This is one generated C++ test in the seq1 family, focused on the `rename-out/destination-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close A/bar; rename A/bar to bar; open bar; fsync bar; checkpoint; close bar. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: destination file fsync after rename out of A. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang287.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang288.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang288.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename A/bar to root bar, then recreate and fsync A/bar. This is one generated C++ test in the seq1 family, focused on the `rename-out/recreate-source` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close A/bar; rename A/bar to bar; recreate A/bar; fsync A/bar; checkpoint; close A/bar. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: source-name recreation after rename out of A. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang288.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang289.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang289.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename A/bar to root bar, then create and fsync A/foo. This is one generated C++ test in the seq1 family, focused on the `rename-out/sibling-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close A/bar; rename A/bar to bar; create A/foo; fsync A/foo; checkpoint; close A/foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: rename out of A plus sibling file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang289.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang290.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang290.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename A/bar to root bar, then fsync mount root. This is one generated C++ test in the seq1 family, focused on the `rename-out/root-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close A/bar; rename A/bar to bar; open mount root as O_DIRECTORY; fsync root directory; checkpoint; close root fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: destination-parent/root directory fsync for rename out of A. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang290.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang291.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang291.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename A/bar to root bar, then create and fsync root foo. This is one generated C++ test in the seq1 family, focused on the `rename-out/unrelated-file-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close A/bar; rename A/bar to bar; create foo; fsync foo; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: rename out of A plus unrelated root file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang291.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang292.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang292.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename A/bar to root bar, then global sync. This is one generated C++ test in the seq1 family, focused on the `rename-out/sync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create and close A/bar; rename A/bar to bar; CmSync; checkpoint. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: rename out of A with global flush. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang292.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang293.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang293.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename directory A to B, recreate A, then fsync new A. This is one generated C++ test in the seq1 family, focused on the `directory-rename/recreate-and-fsync-new` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; open and close A directory; rename A to B; mkdir new A; open new A as O_DIRECTORY; fsync new A; checkpoint; close A fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: directory rename plus same-name directory recreation. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang293.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang294.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang294.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename directory A to B, recreate A, then fsync mount root. This is one generated C++ test in the seq1 family, focused on the `directory-rename/root-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; open and close A directory; rename A to B; open mount root as O_DIRECTORY; fsync root directory; checkpoint; close root fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: directory rename namespace durability through root fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang294.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang295.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang295.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename directory A to B, recreate A, then fsync B. This is one generated C++ test in the seq1 family, focused on the `directory-rename/destination-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; open and close A directory; rename A to B; open B as O_DIRECTORY; fsync B; checkpoint; close B fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: directory rename destination fsync after recreation of source name. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang295.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang296.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang296.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for rename directory A to B, then global sync. This is one generated C++ test in the seq1 family, focused on the `directory-rename/sync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; open and close A directory; rename A to B; CmSync; checkpoint. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: directory rename durability under sync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang296.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang297.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang297.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for set user.xattr1 on root foo, then fsync mount root. This is one generated C++ test in the seq1 family, focused on the `xattr-set/root-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; fsetxattr user.xattr1=val1 on foo; open mount root as O_DIRECTORY; fsync root directory; checkpoint; close foo and root fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: xattr persistence with directory fsync instead of file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang297.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang298.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang298.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for set user.xattr1 on root foo, then fsync foo. This is one generated C++ test in the seq1 family, focused on the `xattr-set/file-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; fsetxattr user.xattr1=val1 on foo; fsync foo; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: xattr persistence through file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang298.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang299.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang299.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for set user.xattr1 on root foo, then create and fsync bar. This is one generated C++ test in the seq1 family, focused on the `xattr-set/unrelated-file-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; fsetxattr user.xattr1=val1 on foo; create bar; fsync bar; checkpoint; close foo and bar. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: xattr update with unrelated file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang299.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang300.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang300.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for set user.xattr1 on root foo, then global sync. This is one generated C++ test in the seq1 family, focused on the `xattr-set/sync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; fsetxattr user.xattr1=val1 on foo; CmSync; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: xattr update durability under sync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang300.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang301.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang301.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for set user.xattr1 on A/foo, then fsync directory A. This is one generated C++ test in the seq1 family, focused on the `nested-xattr-set/parent-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create A/foo; fsetxattr user.xattr1=val1 on A/foo; open A as O_DIRECTORY; fsync A; checkpoint; close A/foo and A fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: nested-file xattr persistence with parent directory fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang301.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang302.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang302.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for set user.xattr1 on A/foo, then fsync A/foo. This is one generated C++ test in the seq1 family, focused on the `nested-xattr-set/file-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create A/foo; fsetxattr user.xattr1=val1 on A/foo; fsync A/foo; checkpoint; close A/foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: nested-file xattr persistence through file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang302.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang303.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang303.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for set user.xattr1 on A/foo, then create and fsync A/bar. This is one generated C++ test in the seq1 family, focused on the `nested-xattr-set/sibling-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create A/foo; fsetxattr user.xattr1=val1 on A/foo; create A/bar; fsync A/bar; checkpoint; close A/foo and A/bar. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: nested xattr update with sibling file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang303.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang304.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang304.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for set user.xattr1 on A/foo, then global sync. This is one generated C++ test in the seq1 family, focused on the `nested-xattr-set/sync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create A/foo; fsetxattr user.xattr1=val1 on A/foo; CmSync; checkpoint; close A/foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: nested-file xattr update under sync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang304.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang305.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang305.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for set then remove user.xattr1 on root foo, then fsync mount root. This is one generated C++ test in the seq1 family, focused on the `xattr-remove/root-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; fsetxattr user.xattr1=val1; removexattr user.xattr1 on foo; open mount root as O_DIRECTORY; fsync root directory; checkpoint; close foo and root fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: xattr add/remove cancellation with directory fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang305.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang306.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang306.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for set then remove user.xattr1 on root foo, then fsync foo. This is one generated C++ test in the seq1 family, focused on the `xattr-remove/file-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; fsetxattr user.xattr1=val1; removexattr user.xattr1 on foo; fsync foo; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: xattr removal persistence through file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang306.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang307.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang307.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for set then remove user.xattr1 on root foo, then create and fsync bar. This is one generated C++ test in the seq1 family, focused on the `xattr-remove/unrelated-file-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; fsetxattr user.xattr1=val1; removexattr user.xattr1 on foo; create bar; fsync bar; checkpoint; close foo and bar. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: xattr removal with unrelated file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang307.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang308.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang308.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for set then remove user.xattr1 on root foo, then global sync. This is one generated C++ test in the seq1 family, focused on the `xattr-remove/sync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; fsetxattr user.xattr1=val1; removexattr user.xattr1 on foo; CmSync; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: xattr removal under sync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang308.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang309.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang309.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for set then remove user.xattr1 on A/foo, then fsync directory A. This is one generated C++ test in the seq1 family, focused on the `nested-xattr-remove/parent-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create A/foo; fsetxattr user.xattr1=val1; removexattr user.xattr1 on A/foo; open A as O_DIRECTORY; fsync A; checkpoint; close A/foo and A fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: nested xattr add/remove with parent directory fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang309.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang310.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang310.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for set then remove user.xattr1 on A/foo, then fsync A/foo. This is one generated C++ test in the seq1 family, focused on the `nested-xattr-remove/file-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create A/foo; fsetxattr user.xattr1=val1; removexattr user.xattr1 on A/foo; fsync A/foo; checkpoint; close A/foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: nested xattr removal through file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang310.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang311.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang311.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for set then remove user.xattr1 on A/foo, then create and fsync A/bar. This is one generated C++ test in the seq1 family, focused on the `nested-xattr-remove/sibling-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create A/foo; fsetxattr user.xattr1=val1; removexattr user.xattr1 on A/foo; create A/bar; fsync A/bar; checkpoint; close A/foo and A/bar. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: nested xattr removal with sibling file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang311.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang312.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang312.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for set then remove user.xattr1 on A/foo, then global sync. This is one generated C++ test in the seq1 family, focused on the `nested-xattr-remove/sync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create A/foo; fsetxattr user.xattr1=val1; removexattr user.xattr1 on A/foo; CmSync; checkpoint; close A/foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: nested xattr removal under sync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang312.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang313.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang313.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for write 32 KiB to root foo, truncate to 2500 bytes, then fsync mount root. This is one generated C++ test in the seq1 family, focused on the `truncate/root-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; WriteData(foo, offset 0, length 32768); truncate foo to 2500; open mount root as O_DIRECTORY; fsync root directory; checkpoint; close foo and root fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: file size contraction with only directory fsync after truncation. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang313.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang314.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang314.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for write 32 KiB to root foo, truncate to 2500 bytes, then fsync foo. This is one generated C++ test in the seq1 family, focused on the `truncate/file-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; WriteData(foo, offset 0, length 32768); truncate foo to 2500; fsync foo; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: file size contraction persisted by file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang314.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang315.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang315.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for write 32 KiB to root foo, truncate to 2500 bytes, then create and fsync bar. This is one generated C++ test in the seq1 family, focused on the `truncate/unrelated-file-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; WriteData(foo, offset 0, length 32768); truncate foo to 2500; create bar; fsync bar; checkpoint; close foo and bar. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: truncate plus unrelated file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang315.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang316.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang316.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for write 32 KiB to root foo, truncate to 2500 bytes, then global sync. This is one generated C++ test in the seq1 family, focused on the `truncate/sync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; WriteData(foo, offset 0, length 32768); truncate foo to 2500; CmSync; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: truncate durability under sync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang316.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang317.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang317.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for write 32 KiB to A/foo, truncate to 2500 bytes, then fsync directory A. This is one generated C++ test in the seq1 family, focused on the `nested-truncate/parent-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create A/foo; WriteData(A/foo, offset 0, length 32768); truncate A/foo to 2500; open A as O_DIRECTORY; fsync A; checkpoint; close A/foo and A fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: nested-file truncate with parent directory fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang317.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang318.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang318.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for write 32 KiB to A/foo, truncate to 2500 bytes, then fsync A/foo. This is one generated C++ test in the seq1 family, focused on the `nested-truncate/file-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create A/foo; WriteData(A/foo, offset 0, length 32768); truncate A/foo to 2500; fsync A/foo; checkpoint; close A/foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: nested-file truncate persisted by file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang318.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang319.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang319.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for write 32 KiB to A/foo, truncate to 2500 bytes, then create and fsync A/bar. This is one generated C++ test in the seq1 family, focused on the `nested-truncate/sibling-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create A/foo; WriteData(A/foo, offset 0, length 32768); truncate A/foo to 2500; create A/bar; fsync A/bar; checkpoint; close A/foo and A/bar. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: nested truncate plus sibling file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang319.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang320.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang320.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for write 32 KiB to A/foo, truncate to 2500 bytes, then global sync. This is one generated C++ test in the seq1 family, focused on the `nested-truncate/sync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create A/foo; WriteData(A/foo, offset 0, length 32768); truncate A/foo to 2500; CmSync; checkpoint; close A/foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: nested truncate durability under sync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang320.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang321.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang321.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for create root foo and call fdatasync before checkpoint. This is one generated C++ test in the seq1 family, focused on the `fdatasync/root-file` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo with O_RDWR|O_CREAT; fdatasync foo; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: minimal fdatasync persistence case for a new root file. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang321.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang322.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang322.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for create root foo and call fdatasync before checkpoint. This is one generated C++ test in the seq1 family, focused on the `fdatasync/root-file-duplicate` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo with O_RDWR|O_CREAT; fdatasync foo; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: duplicate generated fdatasync variant for a new root file. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang322.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang323.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang323.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for create root foo and call fdatasync before checkpoint. This is one generated C++ test in the seq1 family, focused on the `fdatasync/root-file-duplicate` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo with O_RDWR|O_CREAT; fdatasync foo; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: duplicate generated fdatasync variant for a new root file. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang323.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang324.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang324.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for create root foo and call fdatasync before checkpoint. This is one generated C++ test in the seq1 family, focused on the `fdatasync/root-file-duplicate` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo with O_RDWR|O_CREAT; fdatasync foo; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: duplicate generated fdatasync variant for a new root file. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang324.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang325.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang325.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for mkdir A, create A/foo, and call fdatasync before checkpoint. This is one generated C++ test in the seq1 family, focused on the `fdatasync/nested-file` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create A/foo with O_RDWR|O_CREAT; fdatasync A/foo; checkpoint; close A/foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: minimal fdatasync persistence case for a new nested file. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang325.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang326.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang326.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for mkdir A, create A/foo, and call fdatasync before checkpoint. This is one generated C++ test in the seq1 family, focused on the `fdatasync/nested-file-duplicate` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create A/foo with O_RDWR|O_CREAT; fdatasync A/foo; checkpoint; close A/foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: duplicate generated fdatasync variant for a new nested file. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang326.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang327.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang327.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for mkdir A, create A/foo, and call fdatasync before checkpoint. This is one generated C++ test in the seq1 family, focused on the `fdatasync/nested-file-duplicate` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create A/foo with O_RDWR|O_CREAT; fdatasync A/foo; checkpoint; close A/foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: duplicate generated fdatasync variant for a new nested file. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang327.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang328.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang328.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for mkdir A, create A/foo, and call fdatasync before checkpoint. This is one generated C++ test in the seq1 family, focused on the `fdatasync/nested-file-duplicate` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: mkdir A; create A/foo with O_RDWR|O_CREAT; fdatasync A/foo; checkpoint; close A/foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: duplicate generated fdatasync variant for a new nested file. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang328.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang28.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang28.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for write 32 KiB to foo, zero a kept-size range beyond EOF, then global sync. This is one generated C++ test in the seq1 family, focused on the `fallocate/past-eof-sync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; WriteData(foo, offset 0, length 32768); fallocate ZERO_RANGE|KEEP_SIZE at offset 32768 length 32768; CmSync; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: zero-range fallocate past the current logical EOF with KEEP_SIZE. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang28.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang29.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang29.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for write 32 KiB to foo, zero first 5000 bytes, then fsync mount root. This is one generated C++ test in the seq1 family, focused on the `fallocate/start-root-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; WriteData(foo, offset 0, length 32768); fallocate ZERO_RANGE|KEEP_SIZE at offset 0 length 5000; open mount root as O_DIRECTORY; fsync root directory; checkpoint; close foo and root fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: zero-range fallocate at file start with directory fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang29.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang3.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang3.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for create foo and bar, then fsync bar. This is one generated C++ test in the seq1 family, focused on the `two-file-create/fsync-second` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; create bar; fsync bar; checkpoint; close foo and bar. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: minimal two-file create case where only one file is fsynced. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang3.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang30.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang30.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for write 32 KiB to foo, zero first 5000 bytes, then fsync foo. This is one generated C++ test in the seq1 family, focused on the `fallocate/start-file-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; WriteData(foo, offset 0, length 32768); fallocate ZERO_RANGE|KEEP_SIZE at offset 0 length 5000; fsync foo; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: zero-range fallocate at file start with file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang30.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang31.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang31.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for write 32 KiB to foo, zero first 5000 bytes, then create and fsync bar. This is one generated C++ test in the seq1 family, focused on the `fallocate/start-unrelated-file-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; WriteData(foo, offset 0, length 32768); fallocate ZERO_RANGE|KEEP_SIZE at offset 0 length 5000; create bar; fsync bar; checkpoint; close foo and bar. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: zero-range fallocate with unrelated file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang31.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang32.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang32.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for write 32 KiB to foo, zero first 5000 bytes, then global sync. This is one generated C++ test in the seq1 family, focused on the `fallocate/start-sync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; WriteData(foo, offset 0, length 32768); fallocate ZERO_RANGE|KEEP_SIZE at offset 0 length 5000; CmSync; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: zero-range fallocate at file start under sync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang32.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang33.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang33.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for write 32 KiB to foo, zero range starting at 30768, then fsync mount root. This is one generated C++ test in the seq1 family, focused on the `fallocate/eof-cross-root-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; WriteData(foo, offset 0, length 32768); fallocate ZERO_RANGE|KEEP_SIZE at offset 30768 length 5000; open mount root as O_DIRECTORY; fsync root directory; checkpoint; close foo and root fd. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: zero-range fallocate crossing the old EOF boundary with directory fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang33.cpp -->
<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang34.cpp -->
# sources/test-tools/crashmonkey/code/tests/seq1/j-lang34.cpp

Purpose: Exercises CrashMonkey crash-consistency behavior for write 32 KiB to foo, zero range starting at 30768, then fsync foo. This is one generated C++ test in the seq1 family, focused on the `fallocate/eof-cross-file-fsync` scenario.

Important APIs/types/functions: BaseTestCase virtual methods setup(), run(int checkpoint), and check_test(); CrashMonkey wrapper calls cm_->CmOpen, CmClose, CmFsync, CmFdatasync, CmRename, CmSync, and CmCheckpoint; POSIX calls include mkdir plus the scenario-specific fallocate, truncate, fsetxattr, or removexattr when present. Paths are stored as std::string members derived from mnt_dir_.

Control flow: setup() initializes all path members from mnt_dir_. run() repeats that initialization, sets local_checkpoint to zero, then performs: create foo; WriteData(foo, offset 0, length 32768); fallocate ZERO_RANGE|KEEP_SIZE at offset 30768 length 5000; fsync foo; checkpoint; close foo. After CmCheckpoint succeeds, it increments local_checkpoint and can return 1 to tell the harness to stop at checkpoint 1; otherwise it closes remaining descriptors and returns 0. check_test() has no file-content or metadata assertions of its own.

State and persistence behavior: zero-range fallocate crossing the old EOF boundary with file fsync. State is confined to the mounted test directory and the CrashMonkey checkpoint stream. setup() and run() rebuild canonical paths for /A, /B, /foo, /bar, A/foo, A/bar, B/foo, B/bar, A/C/foo, and A/C/bar. run() executes one mutation sequence, calls exactly one CmCheckpoint, increments local_checkpoint, and returns 1 when the requested crash point is reached. check_test() only reconstructs paths and returns 0, so oracle comparison is delegated to the surrounding CrashMonkey harness rather than local assertions.

Dependencies and integration points: The test is exported through extern "C" test_case_get_instance() and test_case_delete_instance(), allowing the CrashMonkey loader to instantiate this generated class polymorphically as a BaseTestCase. It depends on Linux/POSIX headers for file, directory, allocation, truncate, and xattr behavior and on user_tools/api/workload.h for WriteData in data-writing cases.

Risks and edge cases: The main risks are weak local oracle coverage, repeated generated boilerplate, and subtle differences between file fsync, directory fsync, fdatasync, and global sync semantics. Error paths return errno immediately; some open-failure branches call CmClose on a negative descriptor, so harness wrappers must tolerate that generated pattern. Because the checkpoint happens before final close in many cases, the harness is specifically probing crash images at the post-sync/pre-close boundary.

Test signals: A successful normal run returns 0 and a successful checkpoint-interrupted run returns 1 at checkpoint 1. Failures surface as negative CrashMonkey wrapper results, POSIX errno returns, failed checkpoint creation, loader failures for the extern C factory functions, or downstream CrashMonkey/replay mismatches for the persisted namespace, data blocks, xattrs, or file size.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/tests/seq1/j-lang34.cpp -->
