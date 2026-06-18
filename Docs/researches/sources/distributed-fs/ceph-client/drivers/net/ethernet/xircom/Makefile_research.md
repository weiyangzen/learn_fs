<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xircom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xircom/Makefile

Purpose: Connects the Xircom vendor directory to the 16-bit PCMCIA Xircom Ethernet driver object.

Important APIs/types/functions: `obj-$(CONFIG_PCMCIA_XIRC2PS) += xirc2ps_cs.o` is the only build rule.

Control flow: Kbuild includes `xirc2ps_cs.o` as built-in or module according to the value of `CONFIG_PCMCIA_XIRC2PS`; if the symbol is disabled, the directory contributes no object.

State and persistence behavior: No runtime state. The file is a build-routing artifact.

Dependencies and integration points: Depends on `PCMCIA_XIRC2PS` from the sibling Kconfig and on `xirc2ps_cs.c` exporting the PCMCIA driver module.

Risks and test signals: Build tests should verify `CONFIG_PCMCIA_XIRC2PS=m` produces `xirc2ps_cs.ko`, built-in links cleanly, and disabled config does not compile the legacy I/O-port driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xircom/Makefile -->
