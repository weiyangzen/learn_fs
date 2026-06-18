# sources/compression/lz4/contrib/gen_manual/gen-lz4-manual.sh

## Purpose
This shell script is a lightweight manual-generation wrapper. It extracts the LZ4 library version from `../../lib/lz4.h`, reports it, and runs the `gen_manual` executable against `lz4.h` and `lz4frame.h`.

## Important APIs, Commands, and Variables
The script uses `sed` to compute `LIBVER_MAJOR_SCRIPT`, `LIBVER_MINOR_SCRIPT`, and `LIBVER_PATCH_SCRIPT`, then builds `LIBVER_SCRIPT`. It calls `./gen_manual` twice with labels `lz4 <version>` and `lz4frame <version>`.

## Control Flow
Execution is linear: parse the version macros, echo `LZ4_VERSION=<version>`, generate `./lz4_manual.html`, then generate `./lz4frame_manual.html`. There is no argument parsing and no explicit error handling.

## State and Persistence
The script writes two HTML files in the current directory, unlike the Makefile target which writes into `../../doc`. It does not create temporary files or maintain state.

## Dependencies and Integration Points
It depends on `/bin/sh`, `sed`, the relative header paths, and a previously built `gen_manual` executable in the same directory. It is integrated with the same comment convention expected by `gen_manual.cpp`.

## Risks
Because there is no `set -e`, a failed version extraction or generator invocation may not halt the whole script in a clearly visible way. Its output paths differ from the Makefile's documented manual paths, so users must know whether they want local HTML files or the docs tree updated.

## Test Signals
Run it from `contrib/gen_manual` after building `gen_manual`; expect an echoed version and non-empty `lz4_manual.html` and `lz4frame_manual.html`.
