# sources/distributed-fs/ceph-client/arch/um/kernel/skas/stub_exe_embed.S

## Purpose
Embeds the built `arch/um/kernel/skas/stub_exe` binary into UML kernel init data so runtime code can materialize it without relying on an external file.

## Important APIs, Types, and Functions
Defines global data symbols `stub_exe_start` and `stub_exe_end` around an `.incbin` of the stripped stub executable. Uses `SYM_DATA_START`, `SYM_DATA_END_LABEL`, `__INITDATA`, and `__FINIT`.

## Control Flow, State, and Persistence
No executable control flow exists here. The embedded byte range is init data consumed by `init_stub_exe_fd()` in `os-Linux/skas/process.c`, which writes it to a memfd or temporary executable file.

## Dependencies and Integration Points
Depends on the SKAS Makefile rule that builds `stub_exe` before this object. Integrates with linker sections and the runtime stub executable loader.

## Risks and Test Signals
Risks are missing rebuild dependencies, wrong symbol visibility, or section placement causing the embedded bytes to be discarded too early. Test clean incremental builds and runtime `uml-userspace` startup from the embedded range.
