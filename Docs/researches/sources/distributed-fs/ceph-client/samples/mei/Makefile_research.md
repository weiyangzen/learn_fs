# sources/distributed-fs/ceph-client/samples/mei/Makefile

Purpose: builds the Intel MEI AMT version user-space sample.

Important APIs/functions: `userprogs-always-y += mei-amt-version`; includes exported UAPI headers.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: MEI UAPI headers and sample user build support.

Risks: runtime requires `/dev/mei*` and an AMT host interface client.

Test signals: samples build should produce `mei-amt-version`.
