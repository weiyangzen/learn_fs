
# sources/distributed-fs/openafs/src/util/dirent_nt.h

Purpose: `dirent_nt.h` supplies a minimal Windows-compatible `DIR` and `struct dirent` interface for OpenAFS utility code that expects POSIX directory iteration.

Important APIs and types: `struct dirent` contains only `char *d_name`. `DIR` wraps a Windows search `HANDLE`, `WIN32_FIND_DATA`, cached current dirent, and `first` flag. Prototypes are `opendir()`, `closedir()`, and `readdir()`.

Control flow and integration: consumers can compile directory traversal code against POSIX-like names while the Windows implementation maps to FindFirst/FindNext APIs in a companion source file.

State and persistence: `DIR` instances store the live Windows handle and current result. No global state is declared here.

Risks and test signals: this is a deliberately partial dirent API; fields such as inode, type, and record length are absent. Tests should cover first-entry behavior, close-after-open, missing directories, wildcard/path handling, and consumers that only rely on `d_name`.
