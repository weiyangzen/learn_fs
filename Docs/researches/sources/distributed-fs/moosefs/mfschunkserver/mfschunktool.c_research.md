# sources/distributed-fs/moosefs/mfschunkserver/mfschunktool.c

## Purpose
`mfschunktool.c` is a standalone check/repair utility for MooseFS chunk files and disk trees. It validates names, headers, CRC tables, and data blocks; it can repair headers/CRCs, rename files from header data, and move damaged chunks aside.

## Important APIs and control flow
Mode flags are fast check, empty-block checking, name repair, and repair. `hdd_check_filename()` parses canonical `chunk_<id>_<version>.mfs` names. `chunk_repair()` validates or repairs one file. `recursive_scan()` walks valid MooseFS disk trees while avoiding active disks by locking `.lock`. `move_file()` handles cross-device movement.

`main()` parses `-f`, `-r`, `-n`, `-e`, `-x`, and `-m`, initializes CRC support, resolves paths, and scans each target. Full checks read all 1024 blocks and compare CRCs; fast checks only validate the last data block and selected empty-block CRCs.

## State, persistence, and risks
Check mode is read-only. `-r` may rewrite chunk headers and CRC blocks; `-n` may rename files; `-m` moves damaged chunks to a target directory. Tests should cover bad names, bad headers, mismatched id/version, 1024 vs 4096 header sizes, truncated files, empty-block CRC variants, active `.lock` detection, `EXDEV` moves, and repair vs check-only behavior.
