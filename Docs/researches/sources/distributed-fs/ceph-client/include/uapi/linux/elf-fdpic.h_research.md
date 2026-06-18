## sources/distributed-fs/ceph-client/include/uapi/linux/elf-fdpic.h

Purpose: This header defines load-map structures for FDPIC ELF executables, libraries, and interpreters. FDPIC supports position-independent execution on systems without a traditional MMU.

Important APIs and types: It includes `linux/elf.h`, defines `PT_GNU_STACK` using the OS-specific program-header range, and declares 32-bit and 64-bit FDPIC load segment and load map structures. Each load segment records mapped core address, file virtual address, and memory size. Load maps carry a version, segment count, and flexible segment array. Both version constants are zero.

Control flow and state: During exec or dynamic loading, the loader maps each segment and records the mapping in an FDPIC load map so runtime code can translate between file VMAs and actual addresses. The header only defines the ABI structures.

Persistence and dependencies: Load maps are runtime process metadata. The persistent input is the ELF/FDPIC file. The header depends on ELF base types and program-header constants.

Integration points: It integrates with architecture-specific FDPIC binfmt support, dynamic loaders, debuggers, and core-dump tooling on FDPIC-capable architectures.

Risks and test signals: Risks include flexible-array sizing errors, 32/64-bit mismatch, version handling, duplicate `PT_GNU_STACK` definition consistency with `elf.h`, and incorrect address translation. Tests should execute FDPIC binaries with multiple segments, inspect load maps, validate core/debugger interpretation, and cover empty or malformed segment counts.
