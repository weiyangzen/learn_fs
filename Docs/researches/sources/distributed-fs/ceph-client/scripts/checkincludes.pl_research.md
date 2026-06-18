# sources/distributed-fs/ceph-client/scripts/checkincludes.pl

## Purpose
`checkincludes.pl` detects duplicate `#include` directives and can optionally remove earlier duplicates in place.

## APIs, Types, And Functions
It uses Perl strict mode, `usage()`, a `-r` option flag, `%includedfiles` counts, and stored `@file_lines`. The include regex matches `<...>` and `"..."` forms.

## Control Flow
Without `-r`, the script counts includes per file and prints duplicate diagnostics. With `-r`, it rewrites each file, suppressing duplicate include lines until only one instance remains, then prints the number removed.

## State And Persistence
In reporting mode, state is memory-only. In remove mode, it persistently rewrites input files.

## Dependencies And Integration Points
It depends on Perl and straightforward preprocessor syntax. It integrates with source cleanup workflows and should be used cautiously around conditional includes.

## Risks And Test Signals
Risks include ignoring macro/ifdef semantics and rewriting files destructively under `-r`. Test signals include duplicate diagnostics in normal mode and reduced include count with a removal summary in `-r` mode.
