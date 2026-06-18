## sources/distributed-fs/ceph-client/arch/s390/kernel/vmlinux.lds.S

Purpose: Linker script for the s390 kernel image, defining executable/data/init/percpu/BSS layout, special low-memory AMODE31 sections, stack-protector/nospec patch tables, boot-data metadata, and relocation assertions.

Important sections and symbols: `_stext`, `_etext`, `_sdata`, `__start_ro_after_init`, `__end_ro_after_init`, `.skey_region_table`, `BOOT_DATA_PRESERVED`, `.amode31.refs`, `__init_begin/end`, `.altinstructions`, `.stack_prot_table`, `.nospec_*_table`, `_samode31`, `_eamode31`, `.vmlinux.info`, and assertions for `.got.plt`, `.plt`, and `.rela.dyn`.

Control flow: The linker starts at `TEXT_OFFSET`, lays out text/rodata/data, separates ro-after-init, includes runtime data and boot-preserved blocks, emits init/exit/alternative tables, reserves fixed-size AMODE31 text/ex-table/data below the required range, emits init/percpu/BSS, includes debug/modinfo metadata, asserts absence of runtime PLT/relocations, and emits a zero-based `.vmlinux.info` structure consumed by the decompressor.

State and persistence: Produces the persistent kernel image layout and many symbols consumed by boot, decompressor, crash dump, stack protector, alternatives, KASAN, and AMODE31 code.

Dependencies and integration: Includes generic and s390 linker macros, ftrace linker fragments, page/thread constants, stack protector code, `text_amode31.S`, decompressor `vmlinux_info`, vmcore metadata, and build-time assertions.

Risks and test signals: Risks include section misalignment, AMODE31 overflow, unexpected relocations/PLT entries, missing stack protector/nospec tables, and decompressor metadata drift. Test signals are link-time assertions, `readelf` layout checks, boot success, stack protector patching, AMODE31 DIAG helpers, and vmcore info address ranges.
