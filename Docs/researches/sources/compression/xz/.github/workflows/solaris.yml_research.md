# sources/compression/xz/.github/workflows/solaris.yml

## Purpose
This workflow validates XZ on Solaris 11.4 with GCC through a VM action. It covers autotools bootstrap, configure, and test execution on Solaris-specific libc and shell paths.

## Important Control Flow
The job checks out the repo, runs `vmactions/solaris-vm`, prints `uname`, notes PATH because `/usr/xpg4/bin` is not default, runs `./autogen.sh --no-po4a`, configures debug + Werror without static libraries, and runs `make check`.

## State, Dependencies, and Integration
Dependencies are the pinned Solaris VM action and the image's preinstalled tools. It integrates with autotools and Solaris portability code such as system extension macros and possible `librt` use.

## Risks and Test Signals
The workflow gives valuable Solaris build/test signal but has no explicit package installation step, so image drift matters. It also skips po4a and has a 10-minute timeout.
