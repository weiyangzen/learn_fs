# sources/distributed-fs/coda/coda-src/asrlauncher/Makefile.am

Purpose: Automake recipe for the newer `asrlauncher` client-side helper.

Important APIs/build targets: Conditionally builds `sbin_PROGRAMS = asrlauncher` from `asrlauncher.c` when `BUILD_CLIENT` is enabled.

Control flow: This is a minimal build declaration without custom rules.

State and persistence: Build metadata only.

Dependencies and integration: Places `asrlauncher` in sbin for client builds; the source includes Coda configuration headers and standard libc/process APIs.

Risks and test signals: Conditional build means coverage depends on client build configuration.
