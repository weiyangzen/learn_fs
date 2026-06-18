# sources/distributed-fs/ceph-client/include/linux/elfcore-compat.h

Purpose: 32-bit compatibility layouts for ELF core notes emitted by a 64-bit kernel for compat tasks.

Important APIs/types/functions: `struct compat_elf_siginfo`, `struct compat_elf_prstatus_common`, `struct compat_elf_prpsinfo`, architecture include hook `CONFIG_ARCH_HAS_ELFCORE_COMPAT`, and `struct compat_elf_prstatus`.

Control flow: compat coredump code fills these structures from task/signal/register state so user-space debuggers see the ABI-correct 32-bit core layout.

State/persistence: persistent only as generated core file contents. Runtime use is transient during coredump.

Dependencies/integration: `linux/elf.h`, native `elfcore.h`, `linux/compat.h`, architecture compat gregset definitions, signal/task coredump paths.

Risks/test signals: risks are layout drift from native definitions, hard-coded `pr_fname[16]` ABI, wrong compat time/pid/uid sizes, and missing arch compat register definitions. Test compat process coredumps, gdb/readelf decoding, register note sizes, and mixed 32-bit userspace on 64-bit kernels.
