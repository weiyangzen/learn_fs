# sources/distributed-fs/ceph-client/samples/pidfd/Makefile

Purpose: builds the pidfd metadata sample user program.

Important APIs/functions: `usertprogs-always-y += pidfd-metadata`; includes exported UAPI headers.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: pidfd-capable libc/kernel headers and sample user build support.

Risks: variable name `usertprogs-always-y` follows kernel samples conventions but is easy to confuse with `userprogs`.

Test signals: sample build should produce `pidfd-metadata`.
