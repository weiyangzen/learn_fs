# sources/distributed-fs/eos/namespace/ns_quarkdb/tools/InodeToFidTool.cc

## Purpose
`InodeToFidTool.cc` is a tiny diagnostic CLI that converts an encoded file inode back into an EOS file ID.

## Important APIs, Types, and Functions
The tool uses `CLI::App` to require `--inode`, then calls `eos::common::FileId::InodeToFid()` and prints the resulting `fid`.

## Control Flow
`main()` constructs the CLI parser, parses `--inode` into an `unsigned long long`, returns parser errors through `app.exit(e)`, converts the inode, prints a single line, and exits zero.

## State and Persistence Behavior
The tool is deterministic and read-only. It does not contact QuarkDB, access files, or persist output.

## Dependencies and Integration Points
It depends on `common/FileId.hh`, sharing the same inode/fid conversion logic used by resolver and etag code paths. It is operationally useful for debugging inode strings or FST metadata.

## Risks and Edge Cases
The command description mistakenly mirrors the fid-to-path tool text. It accepts any unsigned integer the CLI parser allows, including values that may decode to zero or non-file container encodings. Validation is delegated entirely to `FileId::InodeToFid()`.

## Test Signals
Known old-encoding and new-encoding inode samples should be tested, along with zero, container-like inode values, and missing-argument CLI behavior.
