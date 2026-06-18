## sources/distributed-fs/ceph-client/include/linux/build-salt.h

**Purpose:** This header emits a Linux ELF note containing `CONFIG_BUILD_SALT`, allowing builds to carry a configured salt value in the image metadata.

**Important APIs/types/functions:** `LINUX_ELFNOTE_BUILD_SALT` is the note type. `BUILD_SALT` expands differently for assembler and C: assembler uses `ELFNOTE(Linux, ..., .asciz CONFIG_BUILD_SALT)`, while C uses `ELFNOTE32("Linux", ..., CONFIG_BUILD_SALT)`.

**Control flow, state, persistence:** There is no runtime control flow. The persistent output is a build-time ELF note embedded into the object/image.

**Dependencies/integration:** Depends on `linux/elfnote.h` and `CONFIG_BUILD_SALT`. It is consumed by build/link image metadata rather than runtime code.

**Risks and test signals:** Risks are missing or malformed `CONFIG_BUILD_SALT`, assembler/C macro divergence, and linker scripts dropping the note. Test signals are successful vmlinux/module builds and `readelf -n` verification of the Linux build-salt note.
