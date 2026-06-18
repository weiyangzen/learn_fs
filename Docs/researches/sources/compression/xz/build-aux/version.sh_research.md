# sources/compression/xz/build-aux/version.sh

## Purpose
This shell script extracts the XZ/liblzma version string from `src/liblzma/api/lzma/version.h` without a trailing newline, for use by `configure.ac`.

## Important Control Flow
A `sed -n` program maps stability macros to `alpha`, `beta`, or empty, extracts major/minor/patch/stability define values, then a second `sed` joins four lines into dotted form with the stability suffix. `tr` removes newline, carriage return, and a control byte.

## State, Dependencies, and Integration
It is a pure read/print helper depending on `sed` and `tr`. It integrates autotools version generation with the canonical C API version header.

## Risks and Test Signals
The script is brittle to formatting changes in `version.h`; macro naming or ordering changes would break extraction. Its value is avoiding duplicated version constants.
