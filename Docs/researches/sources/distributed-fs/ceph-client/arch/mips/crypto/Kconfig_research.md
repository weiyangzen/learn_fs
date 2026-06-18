# sources/distributed-fs/ceph-client/arch/mips/crypto/Kconfig

Purpose: creates the MIPS CPU accelerated crypto algorithms menu.

Important behavior: the menu is currently empty between `menu "Accelerated Cryptographic Algorithms for CPU (mips)"` and `endmenu`, so it acts as a placeholder for future MIPS crypto options.

Dependencies and integration: sourced by the architecture Kconfig tree; no symbols are defined here.

Risks and test signals: low functional risk, but adding options here should include dependencies for CPU features and matching Makefile objects. Kconfig parsing should continue to include the empty menu without warnings.
