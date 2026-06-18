<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/generic_pt/common.h -->
# sources/distributed-fs/ceph-client/include/linux/generic_pt/common.h

Purpose: Defines common structures and feature bits for the generic radix page-table framework used by hardware-style page tables.

Important APIs/types/functions: `pt_common` stores encoded top table pointer/level, maximum output and virtual address sizes, and feature bitmap. `PT_TOP_LEVEL_BITS/MASK` define low-bit encoding. `enum pt_features` covers DMA-incoherent table memory, full VA, dynamic top, sign extension, range flush strategies, and a format-private feature start. Format wrappers include `pt_amdv1`, `pt_vtdss`, `pt_riscv_32`, `pt_riscv_64`, and `pt_x86_64`, each embedding `pt_common`; additional enum values describe format-specific features such as encrypted tables, forced coherence, forced writable, and RISC-V Svnapot 64K.

Control flow: Format-specific code stores common capability/configuration in `pt_common`; generic algorithms inspect feature bits to validate addresses, update top levels, flush ranges, and choose format behavior.

State and persistence behavior: Page-table runtime state is the encoded root pointer and immutable or slowly changing capability bits. Actual table page allocation is owned by format/algorithm layers.

Dependencies and integration points: Depends on type definitions, build assertions, and bit macros. It is included by generic IOMMU page-table code and format implementations.

Risks: Low-bit pointer encoding requires table pointer alignment. Incorrect feature combinations can produce invalid address validation or unsafe dynamic-top updates. Format-private features share a common start offset and must not collide inside one format.

Test signals: Compile-time layout assertions, feature matrix tests per format, dynamic-top address coverage, sign-extension valid/invalid ranges, and DMA-incoherent flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/generic_pt/common.h -->
