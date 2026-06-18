# sources/distributed-fs/ceph-client/drivers/s390/char/Kconfig

Purpose: defines configuration symbols for s390 character-device drivers, including 3215/3270 terminals, SCLP tty/console variants, HMC drive FTP support, UV userspace API, tape, z/VM monitor/CP/unit-record drivers, and crash dump support dependencies.

Important APIs/types/functions: Kconfig symbols include `TN3270`, `TN3270_FS`, `TN3270_CONSOLE`, `TN3215`, `TN3215_CONSOLE`, `CCW_CONSOLE`, `SCLP_TTY`, `SCLP_CONSOLE`, `SCLP_VT220_TTY`, `SCLP_VT220_CONSOLE`, `HMC_DRV`, `S390_UV_UAPI`, `S390_TAPE`, `VMLOGRDR`, `VMCP`, `VMCP_CMA_SIZE`, `MONREADER`, `MONWRITER`, and `S390_VMUR`.

Control flow: no runtime flow. Configuration choices determine which objects the adjacent Makefile builds and whether terminal/console paths are built in or modular.

State and persistence behavior: the generated kernel `.config` is the only state. Defaults bias many platform facilities to built-in or module when dependencies are available.

Dependencies and integration points: integrates with CCW, TTY, S390, IUCV, CMA, CRC16, and terminal console selections. `HMC_DRV` selects `CRC16` for FTP command parsing.

Risks and test signals: console symbols require built-in availability in some cases, especially `TN3270_CONSOLE` depending on `TN3270=y`. Test allmodconfig, built-in console configs, dependency-disabled configs, and modular HMC/tape/vm drivers.
