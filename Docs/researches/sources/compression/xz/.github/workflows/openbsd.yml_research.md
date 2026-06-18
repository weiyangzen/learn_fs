# sources/compression/xz/.github/workflows/openbsd.yml

## Purpose
This workflow validates XZ on OpenBSD using autotools. It is especially relevant for pledge sandboxing, OpenBSD SHA-256 interfaces, and autoconf/automake versioned tooling.

## Important Control Flow
The job starts `vmactions/openbsd-vm`, installs versioned autoconf and automake plus gettext/libtool/m4, exports `AUTOCONF_VERSION` and `AUTOMAKE_VERSION`, runs `./autogen.sh --no-po4a`, configures debug + Werror with `--disable-nls --enable-external-sha256`, and runs `make -j4 check`.

## State, Dependencies, and Integration
Dependencies include pinned VM action and OpenBSD packages. State is ephemeral. It integrates with autotools and platform feature detection for external SHA and sandboxing.

## Risks and Test Signals
This is strong OpenBSD portability coverage but skips NLS and po4a. External SHA-256 makes it sensitive to OS crypto API changes.
