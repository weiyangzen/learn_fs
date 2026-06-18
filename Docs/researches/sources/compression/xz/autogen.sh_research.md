# sources/compression/xz/autogen.sh

## Purpose
This script bootstraps the autotools build files from a source checkout and optionally generates translated man pages with po4a.

## Important Control Flow
Under `set -e -x`, it runs `autopoint`, `libtoolize` or `glibtoolize`, `aclocal -I m4`, `autoconf`, `autoheader`, and `automake -acf --foreign`. It parses `--no-po4a` to skip translated man-page generation; otherwise it enters `po4a` and runs `sh update-po`.

## State, Dependencies, and Integration
The script generates or updates `configure`, `Makefile.in`, gettext infrastructure, libtool files, and po4a outputs. Dependencies are GNU autotools, gettext autopoint, libtoolize/glibtoolize, and optionally po4a. Many CI workflows call this before autotools configure.

## Risks and Test Signals
The script is intentionally simple and fail-fast. Tool version differences can change generated files, while `--no-po4a` is important for platforms lacking po4a. It has no cleanup behavior and assumes it is run from the repository root.
