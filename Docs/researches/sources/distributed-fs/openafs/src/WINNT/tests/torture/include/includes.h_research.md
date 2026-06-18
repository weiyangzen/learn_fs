# sources/distributed-fs/openafs/src/WINNT/tests/torture/include/includes.h

Purpose: central portability include for the Windows torture code.

Important APIs and types: sets `_WIN32_WINNT` to `0x0500` if unset, includes Windows, CRT, process, I/O, and time headers, undefines `HAVE_KRB5`, maps `uint16` to `int` and `uint32` to `DWORD`, then includes `proto.h`.

Control flow: none.

State and persistence: none.

Dependencies and integration: intended as the first shared include for `nbio.c` and related torture sources. The mutual include relationship with `proto.h` is guarded by include guards.

Risks and test signals: the local typedef macros can conflict with modern fixed-width integer headers. `_WIN32_WINNT` locks feature availability to Windows 2000-era APIs unless overridden. Build success and prototype visibility are the useful checks.
