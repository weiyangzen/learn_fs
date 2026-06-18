# sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_b.c

Purpose: this file supports the BCMA ChipCommon B unit, primarily exposing an MII management write path through an additional mapped register block.

Important APIs, types, and functions: `bcma_chipco_b_mii_write` writes an MII offset and value with busy-bit waits. `bcma_core_chipcommon_b_init` maps the secondary core address into `ccb->mii`; `bcma_core_chipcommon_b_free` unmaps it. Internal `bcma_wait_reg` polls an MMIO address until masked bits match.

Control flow: init is guarded by `setup_done`, then maps `core->addr_s[1]` for `BCMA_CORE_SIZE` and returns `-ENOMEM` on failure. MII writes write the control register, wait for busy clear, write command data, and wait again. Free unmaps only when a mapping exists.

State and persistence: runtime state is `ccb->setup_done` and `ccb->mii`. Hardware MII management registers persist the side effects of writes.

Dependencies and integration points: it uses raw `readl`/`writel`, `ioremap`/`iounmap`, BCMA logging, and ChipCommon B register offsets. Network/PHY-related code can use the exported MII write helper.

Risks: the wait helper logs timeout but `bcma_chipco_b_mii_write` does not propagate failure, so callers cannot distinguish timed-out hardware from success. Mapping the wrong secondary address would make all MII operations unsafe. Repeated init after failed mapping leaves `setup_done` set before mapping, preventing retry.

Test signals: hardware PHY configuration success and absence of MII timeout logs are the main signals. Fault tests should verify behavior when `ioremap` fails and when busy never clears.
