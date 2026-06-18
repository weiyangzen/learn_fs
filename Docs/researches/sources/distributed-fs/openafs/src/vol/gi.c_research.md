# sources/distributed-fs/openafs/src/vol/gi.c

Purpose: small legacy utility for opening and dumping a raw inode from a mounted inode-fileserver partition. It is not supported on NT or NAMEI builds.

Important APIs/types/functions: `Perror` formats a message into a fixed buffer and passes it to `perror`. `main` parses optional `-stat`, requires a partition path and inode number, stats the partition to obtain `st_dev`, opens the inode with `iopen(dev, inode, 0)`, and either prints inode metadata via `fstat` or streams the inode contents to stdout.

Control flow: argument parsing is linear. Unsupported platforms exit with an explanatory error. On supported builds, failures to stat/open/fstat exit nonzero; otherwise the program loops `read(fd, buf, sizeof(buf))` and writes each block to fd 1.

State and persistence: no persistent writes. It reads arbitrary inode content and may write that content to stdout. `statflag` is a global command option.

Dependencies: legacy inode syscall `iopen`, POSIX `stat`, `fstat`, `read`, `write`, and OpenAFS component version linkage. It assumes inode-based vice partitions, not NAMEI file layout.

Integration points: operator/debug tool for inode-level investigation outside the normal volume package. The output can be redirected to inspect special volume files or vnode data.

Risks: uses `atoi` for inode parsing and `int` fields in printf, so large inode/stat values may truncate. `Perror` uses `sprintf` into a 200-byte stack buffer. No short-write handling is present when dumping to stdout. Running it on the wrong partition/inode can expose raw data without volume-level checks.

Test signals: usage errors, unsupported build branch, valid inode dump, `-stat` output, failed partition stat, failed `iopen`, failed `fstat`, and stdout short-write/error behavior under injected write failures.
