# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/internal.h

Purpose: defines the private interface and shared data contracts for the x86 MCE implementation.

Important APIs and types: declares severity levels, event-list nodes, genpool functions, decoder chain, Intel/AMD/threshold/APEI/injection hooks with stubs for disabled configs, storm tracking structures, `mca_config`, `mce_vendor_flags`, per-bank `struct mce_bank`, vendor helpers, and MSR helpers. `mce_cmp()` defines duplicate equivalence by bank/status/address/misc. `smca_extract_err_addr()` normalizes SMCA error addresses based on bank configuration. `mca_msr_reg()` maps logical bank/register enums to SMCA or legacy MCA MSR addresses.

State and persistence: this header declares global and per-CPU state owned by implementation files: `mca_cfg`, `mce_flags`, bank arrays, bank counts, storm descriptors, CE-disabled banks, and poll hooks. It has no storage except inline behavior.

Dependencies and integration: included by all MCE implementation files and bridges optional Kconfig features while keeping core code buildable with stubs.

Risks and test signals: contract drift can break subtle build combinations or wrong MSR selection. Signals include all relevant Kconfig matrix builds, SMCA and legacy bank access tests, and duplicate/panic-path record behavior.
