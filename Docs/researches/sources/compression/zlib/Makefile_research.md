# sources/compression/zlib/Makefile

Purpose: placeholder Makefile used before `./configure` generates the real build Makefile.

Important targets: `all` prints “Please use ./configure first. Thank you.”; `distclean` delegates to `make -f Makefile.in distclean`.

Control flow: intentionally prevents accidental use of unconfigured make rules while still allowing cleanup through the template Makefile.

State and persistence: `distclean` may regenerate this placeholder after removing configured outputs.

Dependencies and integration: used by the traditional configure flow; overwritten by `configure` from `Makefile.in`.

Risks: users running `make` without configuring receive only a message, not a build. The `distclean` target depends on `Makefile.in` being present.

Test signals: none beyond basic command behavior.
