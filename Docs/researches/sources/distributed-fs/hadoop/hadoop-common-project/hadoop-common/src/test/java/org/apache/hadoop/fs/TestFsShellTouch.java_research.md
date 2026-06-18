## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShellTouch.java

Purpose: tests FsShell touch commands, including `-touchz`, `-touch`, timestamp parsing, create/no-create behavior, access-time-only and modification-time-only updates, and directory timestamp updates.

Important APIs/types/functions: `FsShell.run`, `LocalFileSystem`, `TouchCommands.Touch.getDateFormat`, `FileStatus.getAccessTime`, `FileStatus.getModificationTime`, `GenericTestUtils.getTempPath`, and shell options `-touchz`, `-touch`, `-c`, `-t`, `-a`, `-m`.

Control flow: static setup creates a local shell rooted in a temp directory. Each test enables checksum verification/writing. `testTouchz` creates a zero-length file, allows repeated touchz, and fails when parent does not exist. `testTouch` checks `-c` on missing files, explicit timestamp creation, access-only, modification-only, both-times updates, missing timestamp failure, and `-c` on an existing file. `testTouchDir` repeats timestamp updates for an existing directory and verifies selective time changes.

State and persistence: creates/deletes local files and directories under the shell working directory. Uses short sleeps to ensure distinct timestamps for directory checks.

Dependencies/integration points: shell command parser, local FS timestamp setters, FileStatus timestamp reporting, and Touch command date format.

Risks and test signals: timestamp precision and filesystem support for access time can vary. The tests compare exact parsed millisecond values, so regressions or platform truncation are visible. Parent existence behavior is an important user-facing contract.
