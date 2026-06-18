# sources/distributed-fs/ceph-client/drivers/ps3/Makefile

Purpose: builds PS3 platform support drivers.

Important rules: `CONFIG_PS3_VUART` builds `ps3-vuart.o`; `CONFIG_PS3_PS3AV` builds composite `ps3av_mod.o` from `ps3av.o` and `ps3av_cmd.o`; `CONFIG_PPC_PS3` builds `sys-manager-core.o`; `CONFIG_PS3_SYS_MANAGER`, `CONFIG_PS3_STORAGE`, and `CONFIG_PS3_LPM` build their respective modules.

Control flow/state: build-only file. It ties PS3 system bus, VUART, system manager, storage, AV, and logical performance monitor objects to Kconfig symbols.

Dependencies/integration: PowerPC PS3 firmware/LV1 environment and PS3 system bus headers.

Risks/test signals: verify object inclusion for built-in vs modules, composite AV object linkage, and dependency ordering for VUART consumers such as system manager.
