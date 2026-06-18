# sources/compression/xz/.github/workflows/haiku.yml

## Purpose
This workflow validates XZ on Haiku through a VM action, covering autotools generation and test execution on a less common target OS.

## Important Control Flow
The job checks out the repo, starts `vmactions/haiku-vm`, installs autotools/gettext/libtool/m4 with `pkgman`, runs `./autogen.sh --no-po4a`, configures `--disable-static --enable-debug --enable-werror`, and executes `make -j4 check`.

## State, Dependencies, and Integration
State is ephemeral in the VM. Dependencies are the pinned Haiku VM action and Haiku package availability. It integrates with autotools portability and core test execution.

## Risks and Test Signals
This provides useful non-POSIX-edge portability signal but skips po4a and has a short timeout. Failures may reflect VM/package drift as much as source regressions.
