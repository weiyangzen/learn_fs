# sources/distributed-fs/ceph-client/samples/nitro_enclaves/Makefile

Purpose: standalone Makefile for the Nitro Enclaves ioctl user-space sample.

Important APIs/functions: builds `ne_ioctl_sample` from `ne_ioctl_sample.c` with `$(CC)`, `-Wall`, and `-lpthread`; provides `clean`.

Control flow: build-only.

State and persistence: generated executable.

Dependencies and integration: pthreads, Nitro Enclaves UAPI headers, and local compiler.

Risks: unlike kbuild `userprogs`, this standalone target must be invoked in its directory or with suitable paths.

Test signals: `make` creates `ne_ioctl_sample`; `make clean` removes it.
