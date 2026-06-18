<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/Kconfig -->
## sources/distributed-fs/ceph-client/arch/mips/generic/Kconfig

**Purpose:** Defines configuration switches for the generic MIPS kernel's legacy boards, FIT-embedded FDTs, and selected SoC/virtual boards.

**Important APIs/types/functions:** Symbols include `LEGACY_BOARDS`, `YAMON_DT_SHIM`, `LEGACY_BOARD_SEAD3`, `LEGACY_BOARD_OCELOT`, `SOC_VCOREIII`, multiple `FIT_IMAGE_FDT_*` options, `BOARD_INGENIC`, and `VIRT_BOARD_RANCHU`.

**Control flow:** Kconfig `select` and `depends on` relationships decide which board C files, DT shims, SOC support, and early printk helpers compile.

**State, dependencies, integration:** Drives `arch/mips/generic/Makefile`, FIT image fragments, and machine registration code.

**Risks and test signals:** `select` can pull low-level support unexpectedly; Ocelot is mutually constrained with SEAD3. Test all board option combinations that the comments call out, especially Ocelot versus SEAD3 and SOC_VCOREIII dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/Kconfig -->
