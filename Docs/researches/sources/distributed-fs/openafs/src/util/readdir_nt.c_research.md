# sources/distributed-fs/openafs/src/util/readdir_nt.c

Purpose: Implements minimal POSIX-like `opendir()`, `readdir()`, and `closedir()` for Windows.

Important APIs: `opendir(const char *path)` opens a `FindFirstFile(path\\*)` handle. `readdir(DIR *dir)` returns a pointer to a reusable `struct dirent` stored inside the `DIR`. `closedir(DIR *dir)` closes the Windows handle and frees the `DIR`.

Control flow and state: `opendir()` handles some Windows errors specially, including checking whether an empty root-like directory exists when `FindFirstFile` reports missing file/path. `readdir()` skips `.` and `..`, advances via `FindNextFile()`, maps errors through `nterr_nt2unix()`, and returns NULL at end. The current find data and dirent live in the `DIR` object.

Dependencies and integration: Includes roken, Windows APIs, `winbase.h`, and `afs/errmap_nt.h`. This supports code written against POSIX directory iteration.

Risks and test signals: `opendir()` uses `strcpy`/`strcat` into `MAX_PATH` storage without length checks. `readdir()` uses assignment in the `while (rc = FindNextFile(...))` condition intentionally but is easy to misread. Directory entries are invalidated by the next `readdir()` call. Tests are indirect through Windows directory traversal consumers.
