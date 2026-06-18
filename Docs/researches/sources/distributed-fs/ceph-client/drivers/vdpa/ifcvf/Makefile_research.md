# sources/distributed-fs/ceph-client/drivers/vdpa/ifcvf/Makefile

Purpose: kbuild composition for the Intel IFC VF vDPA driver.

Important APIs/types/functions: `obj-$(CONFIG_IFCVF) += ifcvf.o`; `ifcvf-$(CONFIG_IFCVF) += ifcvf_main.o ifcvf_base.o`.

Control flow: builds a composite `ifcvf` module from the vDPA bus glue and low-level hardware helper files.

State and persistence: build-only file.

Dependencies and integration: selected from the top-level vDPA Makefile and Kconfig `IFCVF`.

Risks: adding new IFCVF files requires updating the composite object list.

Test signals: module build confirms both `ifcvf_main.o` and `ifcvf_base.o` are linked into `ifcvf.ko`.
