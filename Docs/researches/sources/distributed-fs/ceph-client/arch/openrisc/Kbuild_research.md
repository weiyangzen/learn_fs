# sources/distributed-fs/ceph-client/arch/openrisc/Kbuild

Purpose: adds OpenRISC lib, kernel, and mm subdirectories to the architecture build.

Important APIs/types/functions: Build declarations: `obj-y=lib/ kernel/ mm/`.

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
