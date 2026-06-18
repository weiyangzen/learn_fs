# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/Makefile

Purpose: builds the Broadcom `bnxt_re` RDMA driver object and supplies include paths for shared Broadcom Ethernet headers.

Important build entries: `ccflags-y` adds `drivers/net/ethernet/broadcom/bnxt` to the include path. `obj-$(CONFIG_INFINIBAND_BNXT_RE) += bnxt_re.o` connects the object to the Kconfig symbol. `bnxt_re-y` links `main.o`, `ib_verbs.o`, `qplib_res.o`, `qplib_rcfw.o`, `qplib_sp.o`, `qplib_fp.o`, `hw_counters.o`, `debugfs.o`, and `uapi.o`.

Control flow: no runtime control flow exists. Build control flows from Kbuild expansion of `CONFIG_INFINIBAND_BNXT_RE` into object inclusion.

State and persistence: this file affects build artifacts only. It does not create persistent runtime state.

Dependencies and integration points: integrates with kernel Kbuild, RDMA-core driver build conventions, and the sibling Broadcom Ethernet driver headers. The object list shows the driver’s major subsystems: main device binding, verbs, firmware/resource libraries, stats, debugfs, and user ABI.

Risks: omitting a subsystem object causes link failures or missing callback implementations. The Broadcom include path can hide unintended header dependencies. Object ordering is normally not significant for Kbuild linking but can matter for initcall or symbol expectations if changed carelessly.

Test signals: incremental and clean kernel builds with `CONFIG_INFINIBAND_BNXT_RE=y` and `m`, compile with the underlying `BNXT` driver enabled, and link checks for all exported verbs, debugfs, stats, and uapi symbols.
