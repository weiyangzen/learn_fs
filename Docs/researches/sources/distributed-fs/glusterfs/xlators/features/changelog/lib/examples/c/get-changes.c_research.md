# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/examples/c/get-changes.c

Purpose: this C example demonstrates the simple polling changelog API for one brick. It scans every ten seconds, prints changelog file names, and marks each processed file done.

Important functions and APIs: `main` calls `gf_changelog_init`, `gf_changelog_register`, `gf_changelog_scan`, `gf_changelog_next_change`, and `gf_changelog_done`. The `handle_error` macro prints errno-backed failures.

Control flow: after registration, the loop scans the processing directory, reads entries from the tracker with `gf_changelog_next_change`, simulates processing with comments, and moves each file to processed via `gf_changelog_done`. A zero scan count sleeps and repeats.

State and persistence behavior: the library manages a scratch directory, tracker file, processing directory, and processed directory. This example demonstrates the intended contract that consumers call `done` after processing each changelog file.

Dependencies and integration points: includes `changelog.h` and links with `libgfchangelog`. It is a usage sample for changelog consumers outside the xlator stack.

Risks: the brick path, scratch path, and log path are hardcoded. It does not handle shutdown, retries, or partial processing beyond printing errors. The sample only prints file names and does not parse contents.

Test signals: compile via the documented pkg-config command, run against a brick with changelog enabled, create changes, observe scan count and file names, and confirm processed files are moved after `done`.
