# sources/distributed-fs/ceph-client/samples/fanotify/Makefile

Purpose: builds the fanotify filesystem error monitor user program.

Important APIs/functions: `userprogs-always-y += fs-monitor`; adds exported UAPI include path and `-Wall`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on user-space compile support and fanotify UAPI headers.

Risks: no kernel config guard in this Makefile; runtime requires fanotify support and permission.

Test signals: samples build should produce `fs-monitor`.
