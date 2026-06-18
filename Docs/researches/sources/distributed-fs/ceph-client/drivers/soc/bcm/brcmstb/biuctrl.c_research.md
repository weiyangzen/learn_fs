# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/biuctrl.c

Purpose: Broadcom STB CPU BIU control early init code. It maps the `brcm,brcmstb-cpu-biu-ctrl` register block, selects per-CPU-family register offsets, configures MCP write pairing, read/write credits, MCP flow credits, writeback throttling, and B53/A72 read-ahead cache controls.

Important APIs and functions: `brcmstb_biuctrl_init()` is an `early_initcall`; `setup_hifcpubiuctrl_regs()` maps MMIO and chooses `b15_cpubiuctrl_regs`, `b53_cpubiuctrl_regs`, `b53_cpubiuctrl_no_wb_regs`, or `a72_cpubiuctrl_regs`; `mcp_write_pairing_set()`, `a72_b53_rac_enable_all()`, and `mcp_a72_b53_set()` write the tuning registers. `cbc_readl()` and `cbc_writel()` centralize offset validity and skip RAC writes when `CONFIG_CACHE_B15_RAC` owns RAC handling.

Control flow: init finds the BIU node, maps registers, reads CPU node compatibility, handles the 7260A0 no-writeback-controller exception, applies write-pairing policy from device tree, enables RAC where applicable, and applies A72/B53 MCP tuning for known family IDs. On suspend, syscore ops save all BIU control registers and restore them on resume.

State and persistence: global `cpubiuctrl_base`, `mcp_wr_pairing_en`, selected register offset table, and `cpubiuctrl_reg_save[]` persist for runtime and sleep transitions. Hardware register state is the durable side effect across boot and resume.

Dependencies and integration: depends on OF, MMIO, CPU compatible strings, `brcmstb_get_family_id()`, `BRCM_ID()`/`BRCM_REV()`, optional PM sleep syscore registration, and optional B15 RAC cache driver. It integrates before most drivers through early init because memory bus/cache policy affects broad system behavior.

Risks and test signals: risks include wrong register layout selection, unsupported CPU node, stale family ID if `common.c` early init did not populate it, and suspend/resume restoring sentinel reads from unavailable registers. Test signals are boot logs for MCP/RAC messages, memcpy or memory throughput checks on B53/A72, suspend/resume stability, and absence of unsupported CPU or MMIO mapping errors.
