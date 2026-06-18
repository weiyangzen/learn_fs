# sources/distributed-fs/ceph-client/samples/landlock/Makefile

Purpose: builds the Landlock sandboxer user program and provides convenience `all`/`clean` targets.

Important APIs/functions: `userprogs-always-y := sandboxer`, exported UAPI include path, recursive `make -C ../.. samples/landlock/`, and clean target.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: Linux Landlock UAPI headers and kbuild sample user program support.

Risks: BSD-3-Clause SPDX differs from GPL-heavy samples, matching the source file.

Test signals: `make samples/landlock/` should produce `sandboxer`.
