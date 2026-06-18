# sources/compression/xz/.github/workflows/netbsd.yml

## Purpose
This workflow validates the CMake/Ninja build on NetBSD. It emphasizes generated translations and compiler-warning cleanliness on a BSD platform.

## Important Control Flow
The job checks out the repo, starts `vmactions/netbsd-vm`, installs CMake/gettext/ninja/po4a, runs `./po4a/update-po`, configures CMake with shared libs, debug-like C flags, Werror, and a strict-overflow warning suppression, then runs Ninja and CTest.

## State, Dependencies, and Integration
Dependencies are the pinned NetBSD VM action and packages. It integrates with CMake feature probes, gettext/po4a assets, Ninja build generation, and CTest.

## Risks and Test Signals
It provides signal for NetBSD headers, sysctl/proc detection, and translated man-page generation. It is CMake-only and limited by a 10-minute timeout.
