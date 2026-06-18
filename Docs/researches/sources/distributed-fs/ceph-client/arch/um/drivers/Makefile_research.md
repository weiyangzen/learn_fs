<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/Makefile -->
# sources/distributed-fs/ceph-client/arch/um/drivers/Makefile

Purpose: maps UML driver Kconfig symbols to compiled objects and object groups. It composes multi-object drivers such as vector networking, management console, hostaudio, UBD, port channel, watchdog, RTC, and VFIO, and marks user-mode helper objects for special UML build rules.

Important APIs/types/functions: important object groups are `vector-objs`, `mconsole-objs`, `hostaudio-objs`, `ubd-objs`, `port-objs`, `harddog-objs`, `rtc-objs`, and `vfio_uml-objs`. Important selectors are `obj-y`, `obj-$(CONFIG_*)`, `harddog-builtin-*`, `USER_OBJS`, `CFLAGS_null.o`, and `CFLAGS_xterm.o`.

Control flow: kbuild always builds the stdio console, fd channel, channel core, channel user helpers, and line core. Optional Kconfig symbols append backend and device objects. `USER_OBJS` lets `arch/um/scripts/Makefile.rules` build selected files with `USER_CFLAGS` because they call host libc/syscalls.

State and persistence: no runtime state; output is object composition in the build tree.

Dependencies and integration points: depends on the top-level UML Makefile for `USER_CFLAGS` and `DEV_NULL_PATH`, on channel symbols from `drivers/Kconfig`, and on block/watchdog/random symbols defined in generic subsystem Kconfig files.

Risks: placing a host-helper file outside `USER_OBJS` can compile it with kernel flags and break libc/syscall assumptions. Multi-object grouping must match exported symbols, especially `harddog_user_exp.o` for module builds and `cow_user.o` for common COW parsing.

Test signals: inspect `make V=1 arch/um/drivers/` compile commands, build all listed Kconfig combinations, verify user objects receive host flags, and ensure no unresolved symbols appear when optional drivers are modular or built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/Makefile -->
