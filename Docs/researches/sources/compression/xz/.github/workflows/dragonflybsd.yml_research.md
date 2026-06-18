# sources/compression/xz/.github/workflows/dragonflybsd.yml

## Purpose
This workflow validates XZ on DragonFly BSD through a VM action. It covers autotools bootstrap, configure, and `make check` on a non-Linux BSD platform.

## Important Control Flow
The job runs on Ubuntu, checks out the repo, starts `vmactions/dragonflybsd-vm`, installs autotools/gettext/libtool/m4, runs `./autogen.sh --no-po4a`, configures debug + Werror with a strict-overflow warning suppression, and runs `make -j4 check`.

## State, Dependencies, and Integration
It depends on the pinned VM action, DragonFly package availability, and autotools. All state is inside the VM and runner workspace.

## Risks and Test Signals
The test gives platform-portability signal for DragonFly system APIs and compiler warnings. It has a tight 10-minute timeout and skips po4a, so translated man-page generation is not covered.
