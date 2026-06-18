# sources/distributed-fs/lizardfs/utils/readdir_unlink_test.cc

Purpose: filesystem behavior test for interleaving `readdir()` with `unlink()` in the same directory. It validates that a directory iteration can still remove all previously created entries.

Important APIs/functions: `create_files()` creates numeric empty files. `unlink_files_in_readdir_loop()` opens `"."`, repeatedly calls `readdir()`, skips dot entries, and unlinks each returned file. `remove_empty_dir()` attempts `rmdir()` and treats `ENOTEMPTY` as a logical failure rather than infrastructure error.

Control flow: `main()` optionally accepts file count and workspace path, opens the workspace with `O_PATH|O_DIRECTORY`, `fchdir()`s into it, creates `test-dir`, changes into it, creates files, unlinks while reading, returns to the original directory, and removes `test-dir`. Exit 0 means created count equals unlinked count and `rmdir` succeeded; exit 1 means entries were missed; exit 2 means syscall error.

State and persistence: creates and deletes a temporary `test-dir` in the workspace. On failures, partial files/directories may remain for inspection.

Dependencies/integration: useful for FUSE/distributed directory consistency testing. Depends on Linux `O_PATH`, dirent APIs, and exception wrapping via `std::system_error`.

Risks and test signals: fixed directory name can collide with existing `test-dir`. `sync()` slows tests globally. Test signals are high file counts, workspace errors, ENOTEMPTY failure, and behavior under distributed metadata caching.
