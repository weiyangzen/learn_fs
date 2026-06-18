# sources/distributed-fs/ceph-client/arch/parisc/include/asm/pdcpat.h

Purpose: defines PA-RISC PAT firmware extensions for cell-based 64-bit systems, including interrupt routing, cell/module information, memory descriptors, nonvolatile memory, protection domains, and TOC registration.

Important APIs/types/functions: exports `PDC_PAT_*` procedure/subfunction constants, capability bits, memory descriptor values, `is_pdc_pat()`, `pdc_pat_get_irt_size()`, `pdc_pat_get_irt()`, and PAT return structures such as cell, CPU, and memory PDT info.

Control flow: 64-bit platform setup queries PAT capabilities, retrieves interrupt routing and memory tables, registers TOC vectors, and configures cell/module resources.

State and persistence: PAT-reported topology and memory state persist in kernel platform data; some calls mutate firmware TOC/NVRAM state. Dependencies and integration: depends on `pdc.h`, 64-bit configuration, IOSAPIC, memory discovery, and SMP/cell setup.

Risks and test signals: PAT is firmware ABI-heavy; wrong structure widths break large systems. Test on PAT and non-PAT machines, interrupt routing validation, memory table parsing, and 32-bit fallback behavior.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
