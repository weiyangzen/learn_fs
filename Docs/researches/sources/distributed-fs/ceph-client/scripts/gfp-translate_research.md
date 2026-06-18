# sources/distributed-fs/ceph-client/scripts/gfp-translate

## Purpose
Translates a numeric GFP allocation mask into named `___GFP_*` flag bits using the kernel source tree's own headers.

## APIs, Control Flow, and State
The bash script accepts `--source DIRECTORY`, `-h/--help`, and one mask expression. It guesses the source tree from `/usr/src/linux` or the current directory, creates a temporary C file, extracts bit enum names from `include/linux/gfp_types.h` with `sed`, emits a C program that includes generated autoconf and GFP type headers, compiles it with `${CC:-gcc}`, and runs it. The generated program evaluates `unsigned long long mask = <GFPMASK>` and prints every set bit with a known name or `*** INVALID ***`.

## Dependencies and Integration
It depends on bash, `mktemp`, `sed`, a C compiler, generated kernel config headers, and an in-tree include layout. It is a debugging/diagnostic tool rather than a build dependency.

## Risks and Test Signals
The mask expression is embedded directly into generated C, so this should be treated as local trusted input. It also assumes generated headers exist. Test signals are successful compilation, correct names for known GFP masks, invalid-bit reporting, and cleanup of temporary files on normal or error paths.
