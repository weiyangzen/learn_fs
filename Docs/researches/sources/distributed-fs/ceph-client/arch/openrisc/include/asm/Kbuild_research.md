# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/Kbuild

Purpose: lists generic asm headers and local OpenRISC headers exported or generated for the architecture
include tree.

Important APIs/types/functions: Build declarations: `syscall-y=syscall_table_32.h`, `generic-y=extable.h`, `generic-y=kvm_para.h`,
`generic-y=parport.h`, `generic-y=spinlock_types.h`, `generic-y=spinlock.h`,
`generic-y=qrwlock_types.h`, `generic-y=qrwlock.h`, `generic-y=user.h`.

Control flow: The build system reads this file during Kbuild traversal; object lists and targets determine which
architecture sources are compiled or packaged for the selected configuration.

State and persistence: Persistent effects are build artifacts only: selected objects, generated images, DTBs, or exported
headers. Runtime state is created by the compiled code, not by the make fragment itself.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks are missing objects, stale generated-header dependencies, wrong boot target names, or
configuration drift that silently excludes required architecture code.

Test signals: Test signals are architecture defconfig builds, `make ARCH=... headers_install`, boot image
generation, DTB generation, and allmodconfig coverage for selected options.
