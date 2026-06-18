# sources/distributed-fs/openafs/src/afs/AIX/osi_assem64.s

Purpose: 64-bit variant of the AIX RS/6000 assembly helper routines.

Important APIs and functions: exports the same `get_toc` and `get_ret_addr` entry points as the generic/32-bit files, but uses `.llong` descriptor entries so function descriptors and TOC references are 64-bit wide.

Control flow: both routines are direct register/stack reads followed by branch return. The code path is intentionally minimal because it runs in kernel/module context.

State and persistence: none.

Dependencies and integration: consumed by 64-bit AIX builds of the OpenAFS kernel module, especially the dynamic kernel import code in `osi_config.c`.

Risks and test signals: relies on ABI-stable frame offsets and descriptor layout. Test signals are successful 64-bit link/load and correct import of kernel variables/functions.
