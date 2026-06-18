# sources/distributed-fs/ceph-client/samples/hidraw/Makefile

Purpose: builds the hidraw user-space example.

Important APIs/functions: `userprogs-always-y += hid-example`; includes exported UAPI headers.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on hidraw UAPI headers.

Risks: runtime device compatibility is not represented in the build.

Test signals: samples build should produce `hid-example`.
