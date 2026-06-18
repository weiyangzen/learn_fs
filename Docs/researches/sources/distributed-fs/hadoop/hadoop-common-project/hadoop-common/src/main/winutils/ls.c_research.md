# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/ls.c

Purpose: implements `winutils ls`, a Windows analogue of `ls -ld` that reports file type, permissions, hardlink count, owner, group, size, timestamp, and input path.

Important APIs/functions: `ParseCommandLine` accepts optional `-L` symlink dereference and `-F` pipe-separated output; `GetMaskString` converts Hadoop Unix mask bits to `drwxrwxrwx` text; `LsPrintLine` formats the output; `Ls` drives validation, long-path conversion, metadata lookup, permission lookup, and output. `LsUsage` prints the help text.

Control flow: command-line parsing defaults to `.` when no path is provided, rejects duplicate or unknown options, rejects paths beginning with invalid characters, converts to long-path form, gets handle metadata via `GetFileInformationByName`, gets owner/group/mode via `FindFileOwnerAndPermission`, then prints using the original path string.

State and persistence: no persistent state is changed. It allocates owner/group/long-path buffers and writes a single formatted line to stdout or diagnostics to stderr.

Dependencies/integration: relies on `libwinutils.c` for path, file info, ACL-to-mode, and error reporting; uses the shared `MONTHS` table and `UX_*` constants from `winutils.h`. Called from `main.c` when command is `ls`.

Risks and test signals: exact output spacing and `-F` separator format are compatibility-sensitive. Tests should include regular files, directories, symlinks with and without `-L`, invalid duplicate options, invalid path strings, and ownership or ACL cases that affect the rendered mask.
