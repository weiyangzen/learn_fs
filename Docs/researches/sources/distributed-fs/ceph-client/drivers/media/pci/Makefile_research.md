# sources/distributed-fs/ceph-client/drivers/media/pci/Makefile

Purpose: Kbuild dispatcher for PCI media drivers. It descends into digital-TV and common PCI subdirectories and conditionally builds analog/capture driver directories by config symbol.

Important APIs/types/functions: unconditional `obj-y` descends into `ttpci`, `b2c2`, `pluto2`, `dm1105`, `pt1`, `pt3`, `mantis`, `ngene`, `ddbridge`, `saa7146`, `smipcie`, `netup_unidvb`, and `intel`. Conditional object lines include `VIDEO_BT848`, `VIDEO_COBALT`, `VIDEO_CX18`, `VIDEO_CX23885`, `VIDEO_CX25821`, `VIDEO_CX88`, `VIDEO_DT3155`, `VIDEO_IVTV`, `VIDEO_MGB4`, `VIDEO_SAA7134`, `VIDEO_SAA7164`, `VIDEO_SOLO6X10`, `VIDEO_TW5864`, `VIDEO_TW686X`, `VIDEO_TW68`, and `VIDEO_ZORAN`.

Control flow: Kbuild always visits some subdirectories so their internal Makefiles can gate objects, while other directories are only entered when their config symbol is enabled.

State/persistence: build-only state.

Dependencies/integration: integrates with Kbuild and all PCI media subdriver directories. The comments request alphabetic ordering, though the unconditional list is not purely alphabetical.

Risks/test signals: unconditional descent relies on subdirectories being present and self-gated. Build tests should cover allmodconfig, allyesconfig, randconfig, and selected individual driver configs to catch missing subdir Kconfig/Makefile synchronization.
