# sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso-note.S

Purpose: adds a Linux version note to the SPARC vDSO.

Important APIs/sections: uses `ELFNOTE_START(Linux, 0, "a")`, emits `LINUX_VERSION_CODE`, and closes with `ELFNOTE_END`.

Control flow: assembled into the vDSO so the linker script places it in the PT_NOTE segment.

State and persistence: no runtime state; embeds build-time kernel version metadata into the vDSO image.

Dependencies and integration points: included in the vDSO object list from the Makefile and consumed by userspace/debug tools inspecting PT_NOTE.

Risks: note formatting must match ELF note expectations. Missing notes can affect tooling that identifies the in-memory vDSO.

Test signals: inspect built `vdso64.so.dbg` notes with `readelf -n` and confirm Linux version note is present.
