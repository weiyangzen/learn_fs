# sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso32/vdso-note.S

Purpose: adds a Linux version note to the SPARC32 vDSO image.

Important APIs/sections: emits an allocatable Linux ELF note containing `LINUX_VERSION_CODE`.

Control flow: assembled into the 32-bit vDSO and placed into PT_NOTE by the common layout script.

State and persistence: build-time metadata only.

Dependencies and integration points: included by the vDSO32 link target and used by userspace/debug tooling.

Risks: malformed notes can confuse tools that identify/debug the in-memory vDSO.

Test signals: inspect `vdso32.so.dbg` with `readelf -n` and verify the Linux note exists.
