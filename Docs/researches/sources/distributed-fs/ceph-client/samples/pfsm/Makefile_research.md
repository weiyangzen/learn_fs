# sources/distributed-fs/ceph-client/samples/pfsm/Makefile

Purpose: builds the PFSM wakeup user-space sample.

Important APIs/functions: `userprogs-always-y += pfsm-wakeup`; includes exported UAPI headers.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: PFSM and RTC UAPI/device nodes at runtime.

Risks: runtime device paths are platform-specific.

Test signals: samples build should produce `pfsm-wakeup`.
