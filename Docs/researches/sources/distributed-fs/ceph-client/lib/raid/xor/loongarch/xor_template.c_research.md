# sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_template.c

Purpose: provides the macro template used to generate LoongArch SIMD XOR helpers for multiple vector widths.

Important APIs and flow: expected macros define line width, load/store/XOR operations, and function naming. Generated `XOR_FUNC_NAME(2..5)` loops over `bytes / LINE_WIDTH`, loads the destination line, XORs each source line, stores the destination, and advances all pointers by one line.

State and persistence: no persistence; all behavior is in-place memory transformation.

Dependencies and integration: included from `xor_simd.c` after LSX or LASX macro setup.

Risks and test signals: this file is not standalone, so macro contract changes can silently break both SIMD flavors. Signals are LSX/LASX build failures, disassembly inspection, and KUnit parity checks.
