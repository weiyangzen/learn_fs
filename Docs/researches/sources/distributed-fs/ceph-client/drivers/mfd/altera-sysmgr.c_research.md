<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/altera-sysmgr.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/altera-sysmgr.c

Purpose: implements the Altera/Intel SoCFPGA System Manager regmap provider. It supports direct MMIO access for older system managers and secure-monitor-call mediated access for protected Stratix 10 registers, then exports lookup-by-phandle for other drivers.

Important APIs and functions: exported API is `altr_sysmgr_regmap_lookup_by_phandle(struct device_node *np, const char *property)`. Probe is `sysmgr_probe`. Secure callbacks are `s10_protected_reg_read` and `s10_protected_reg_write`, which issue `arm_smccc_smc` calls with Intel SIP SMC function IDs.

Control flow: core init registers the platform driver. Probe allocates `struct altr_sysmgr`, reads the MMIO resource, computes `max_register`, and either initializes a custom regmap using the physical base as context for `"altr,sys-mgr-s10"` or maps the resource and initializes a fast MMIO regmap otherwise. Lookup resolves a phandle or the node itself, finds the bound platform device by OF node, retrieves `sysmgr->regmap`, drops the device reference, and returns the regmap.

State and persistence: state is a per-device `struct altr_sysmgr` holding only the regmap. Hardware state persists in system manager registers; no cache is configured. The S10 path uses the physical resource start as opaque regmap context for secure calls.

Dependencies and integration points: depends on OF, platform devices, regmap, MMIO mapping, ARM SMCCC, and `linux/mfd/altera-sysmgr.h`. Consumers call the exported lookup helper to share the system-manager regmap without duplicating mappings.

Risks: SMC read writes `result.a1` into `*val` before checking status, so callers must trust the returned status. The lookup helper returns a regmap after `put_device(dev)`; this follows syscon-like lifetime assumptions but relies on the provider staying bound. Probe logs regmap init failure with `pr_err` rather than device context. `devm_ioremap` is used instead of resource-managed exclusive mapping on the non-S10 path.

Test signals: boot on `"altr,sys-mgr"` and `"altr,sys-mgr-s10"` systems, phandle lookup by consumer drivers including probe-defer behavior, SMC success/error paths, register read/write alignment with 32-bit stride, and module unload when built modular.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/altera-sysmgr.c -->
