# sources/distributed-fs/ceph-client/drivers/nfc/Makefile

Purpose: Maps top-level NFC Kconfig symbols to subdirectories and object files built under `drivers/nfc`.

Important APIs, types, and functions: `obj-$(CONFIG_NFC_FDP) += fdp/`, `obj-$(CONFIG_NFC_MICROREAD) += microread/`, `obj-$(CONFIG_NFC_MEI_PHY) += mei_phy.o`, and similar lines select controller families and standalone drivers such as `nfcsim.o`, `port100.o`, `trf7970a.o`, `virtual_ncidev.o`, and vendor subdirectories.

Control flow: There is no runtime flow. Kbuild evaluates the `obj-*` variables from the kernel configuration and descends into selected subdirectories.

State and persistence behavior: Build products are determined by `.config`; no runtime state is affected.

Dependencies and integration points: Integrates with the top-level NFC Kconfig and subordinate Makefiles. Shared helpers such as `mei_phy.o` are built when `CONFIG_NFC_MEI_PHY` is selected by MEI-based HCI drivers.

Risks: Missing or mismatched object names break module builds. Selecting a subdirectory via a core symbol must align with the subdirectory's own Makefile or transport modules can be omitted.

Test signals: Build all affected NFC configs as modules, verify expected `.ko` names, and run `make drivers/nfc/` after Kconfig symbol changes.
