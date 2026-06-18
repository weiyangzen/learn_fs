# sources/compression/xz/.github/workflows/freebsd.yml

## Purpose
This workflow validates XZ on FreeBSD VM releases. It runs autotools bootstrap, configure, and `make check` with debug and Werror.

## Important Control Flow
The matrix defines FreeBSD versions and architectures, then uses `vmactions/freebsd-vm` to install autotools, gettext, libtool, m4, and po4a. The VM runs `./autogen.sh`, `./configure --disable-static --enable-debug --enable-werror`, and `make -j4 check`.

## State, Dependencies, and Integration
Dependencies are the pinned FreeBSD VM action and FreeBSD packages. It integrates with autotools build logic, translated manpage generation through po4a, and the test suite.

## Risks and Test Signals
The matrix currently references `matrix.release` while entries define `version`, which is a workflow risk unless the action defaults compensate. The job is valuable for Capsicum, sysctl, and BSD portability, but constrained by a 10-minute timeout.
