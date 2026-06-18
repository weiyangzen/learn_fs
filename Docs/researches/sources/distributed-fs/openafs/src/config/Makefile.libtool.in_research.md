# sources/distributed-fs/openafs/src/config/Makefile.libtool.in

Purpose: small make fragment that defines suffix rules for modules that build libtool objects.

Important APIs/types/functions: maps `.c.lo`, `%.lo: %.c`, and `.m.lo` to `$(LT_CCRULE)`.

Control flow: included after `Makefile.config` by module Makefiles that need libtool `.lo` output; make suffix/pattern rules invoke the shared libtool compile recipe for C and Objective-C sources.

State and persistence: creates `.lo` and libtool side artifacts controlled by the common `LT_CLEAN` rule.

Dependencies and integration: depends on `LT_CCRULE` from `Makefile.config` and on configured libtool, pthread compiler, and wrappers.

Risks and test signals: risks are rule conflicts with module-specific patterns and Objective-C availability. Libtool library builds and `make clean` removal of `.lo/.libs` artifacts are the signals.
