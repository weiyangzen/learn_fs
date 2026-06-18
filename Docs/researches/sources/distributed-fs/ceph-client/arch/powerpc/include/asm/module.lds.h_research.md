# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/module.lds.h

Purpose: supplies the PowerPC module linker-script fragment that aligns the `.toc` output section.

Important APIs/types/functions: the `SECTIONS` fragment creates `.toc 0 : ALIGN(256)` and collects `*(.got .toc)`.

Control flow: no runtime flow; module linking applies this script fragment.

State and persistence: the module image contains aligned GOT/TOC data used at runtime by relocated code.

Dependencies and integration points: integrates with module linker invocation and PowerPC TOC/GOT relocation ABI.

Risks: incorrect TOC alignment can break TOC-relative addressing or ABI assumptions in module code.

Test signals: build loadable modules, inspect section alignment with `readelf`, and load modules that use TOC/GOT references.
