# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/Makefile

Defines the ERDMA module build target and its constituent object files.

`obj-$(CONFIG_INFINIBAND_ERDMA) := erdma.o` ties the module to the Kconfig option. `erdma-y` links `erdma_cm.o`, `erdma_main.o`, `erdma_cmdq.o`, `erdma_cq.o`, `erdma_verbs.o`, `erdma_qp.o`, and `erdma_eq.o`.

There is no runtime control flow. Kbuild composes the module from the listed translation units. The file's state is build composition; runtime state belongs to the C files.

Integration is with Kbuild and all ERDMA source objects. Risks include unresolved symbols or missing functionality if an object is omitted. Test signals include successful kernel/module builds and symbol resolution across main, CM, command queue, CQ, QP, EQ, and verbs objects.
