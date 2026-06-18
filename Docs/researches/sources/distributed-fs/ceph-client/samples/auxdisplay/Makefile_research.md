# sources/distributed-fs/ceph-client/samples/auxdisplay/Makefile

Purpose: registers the CFAG12864B LCD framebuffer userspace example for kbuild.

Important APIs/types/functions: `userprogs-always-y += cfag12864b-example`.

Control flow: kbuild always builds the named userspace program when the auxdisplay sample directory is selected.

State and persistence: no runtime state; build output is the sample executable.

Dependencies and integration: selected by `CONFIG_SAMPLE_AUXDISPLAY` through `samples/Makefile` and built with kbuild user program rules.

Risks: the Makefile is minimal and relies entirely on default user program build rules.

Test signals: enabling `SAMPLE_AUXDISPLAY` should build `cfag12864b-example` without custom flags.
