# sources/compression/zstd/programs/zstdgrep

## Purpose

This shell script implements `zstdgrep` and alias-compatible `zegrep`/`zfgrep` behavior by decompressing zstd inputs with `zstdcat` and piping them into grep.

## Important APIs, Types, and Functions

Environment variables `GREP` and `ZCAT` override the grep and decompressor commands. The script parses grep options that take arguments, recognizes `-e` and `-f`, handles `--`, `-`, `-h`, and arbitrary short options, and derives extended/fixed grep mode from its executable name.

## Control Flow, State, and Persistence

It first separates grep options from the pattern and file list. With no files, it runs decompression on stdin and greps stdin. With files, it optionally forces `-H` labels for multiple files, then loops over inputs and pipes each decompressed stream to grep with `--label`. Exit status is 1 if any grep invocation fails, otherwise 0.

## Dependencies and Integration Points

It depends on POSIX `sh`, `grep`, and `zstdcat`. CLI tests wrap it through `tests/cli-tests/bin/zstdgrep`.

## Risks and Test Signals

The script builds `grep_args` as a string and intentionally disables globbing around unquoted expansion, so unusual option values with whitespace are risky. `-f` mode ignores the normal pattern and feeds `-` as grep's pattern-file argument. Tests should cover stdin, multiple files with labels, `-e`, `-f`, `-h`, alias names, bad compressed files, and overridden `GREP`/`ZCAT`.
