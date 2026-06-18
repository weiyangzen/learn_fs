<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/missing -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/missing

## Purpose
GNU Automake `missing` helper for crcutil. It provides diagnostic stubs for maintainer tools that may be absent on an end-user build host, allowing generated artifacts to be touched or placeholder outputs to be created when rebuilding from distribution tarballs.

## Important APIs, Types, and Functions
The command line is `missing [OPTION]... PROGRAM [ARGUMENT]...` with `--run`, `--help`, and `--version`. Recognized program families include `aclocal`, `autoconf`, `autoheader`, `autom4te`, `automake`, `bison`/`yacc`, `flex`/`lex`, `help2man`, `makeinfo`, and `tar`. It normalizes `gnu-`, `gnu`, and `g` prefixes and ignores version suffixes when dispatching.

## Control Flow, State, and Persistence
With `--run`, it first executes the requested program and exits on success; exit code `63` is treated as a likely version mismatch and falls through to emulation. Tool-specific cases print warnings explaining which maintainer package is needed, then touch expected outputs such as `aclocal.m4`, `configure`, `config.h.in`, `Makefile.in`, or manual/info files. Parser generators try to copy pre-generated `.c`/`.h` files from nearby sources or create tiny stubs. The `tar` path retries `gnutar`, `gtar`, and then plain `tar` with some nonportable flags removed. Persistent effects are touched timestamps and occasional generated stub files.

## Dependencies and Integration Points
Depends on POSIX shell plus `sed`, `touch`, `find`, `rm`, `cp`, and tar variants. It integrates with Automake-generated dependency rules for the vendored crcutil source; normal builds should rarely execute it unless source timestamps or maintainer files are modified.

## Risks and Test Signals
Risks include hiding missing maintainer dependencies by touching stale generated files, false success for generated stubs that are not semantically valid, unquoted paths in some `touch`/`sed` results, and behavior tied to obsolete Autotools conventions. Test signals include running each supported tool family with and without `--run`, timestamp updates for expected generated files, error behavior for unknown tools and `--version`, parser-generator fallback from existing generated C/H files, and tar fallback on non-GNU systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/missing -->
