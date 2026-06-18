## sources/distributed-fs/orangefs/src/client/webpack/Makefile.am

Purpose: Top-level Automake file for the OrangeFS Apache "webpack" modules.

Important APIs, types, and functions: Defines `ACLOCAL_AMFLAGS=-I m4` and `SUBDIRS=@WP_SUBDIRS@`.

Control flow: During configure, `WP_SUBDIRS` is substituted with the enabled module directories, so `make` recurses only into selected submodules.

State and persistence: No runtime state. Build output depends on configure options and generated Makefiles.

Dependencies and integration points: Integrates with `configure.ac` substitution and the local `m4` macro directory.

Risks and test signals: Empty `WP_SUBDIRS` yields no module builds. Missing `m4` support files or configure substitution breaks autoreconf. Test configure with each enable flag and all combinations, then verify recursive make enters the expected directories only.
