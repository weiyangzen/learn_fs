# sources/distributed-fs/ceph-client/arch/mips/crypto/Makefile

Purpose: placeholder Makefile for MIPS crypto implementation objects.

Important behavior: no objects are currently selected, matching the empty Kconfig menu.

Dependencies and integration: included by the MIPS build when crypto sources are considered. Future accelerated crypto files would be added here under config-specific `obj-*` assignments.

Risks and test signals: no runtime behavior. Build tests should remain unchanged; future additions must pair Kconfig symbols with object names.
