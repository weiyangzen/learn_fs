## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_hw_utils.c

Purpose: common low-level hardware helper functions for Atlantic MMIO access, bitfield updates, descriptor-cache invalidation, error mapping, and TC queue geometry.

Important APIs/types: implements `aq_hw_write_reg_bit()`, `aq_hw_read_reg_bit()`, `aq_hw_read_reg()`, `aq_hw_write_reg()`, 64-bit read/write helpers, `aq_hw_invalidate_descriptor_cache()`, `aq_hw_err_from_flags()`, `aq_hw_num_tcs()`, and `aq_hw_q_per_tc()`.

Control flow: register reads check for all-ones values and confirm against an alive-check register; if both are all ones, the device is marked unplugged. 64-bit access uses native `readq/writeq` when hardware supports 64-bit operations, otherwise lo/hi helpers. Descriptor cache invalidation triggers a hardware toggle then polls for completion. TC helpers translate configured TC mode into counts/queues.

State and persistence: mutates `aq_hw_s.flags` for unplug/hardware errors and writes MMIO registers. No persistent storage.

Dependencies/integration: called by chip-specific hardware layers and higher-level helpers. Depends on `aq_nic_cfg_s` capability data and `hw_atl_llh` low-level descriptor-cache functions.

Risks: all-ones MMIO detection is a common unplug signal but can misclassify if alive-check address is wrong. `aq_hw_write_reg_bit()` relies on masks/shifts supplied by generated low-level code. Descriptor-cache poll timeout return is not directly captured in the shown code, so callers mainly see existing flag-derived errors.

Test signals: MMIO read/write smoke tests, hot-unplug/error simulation, descriptor-cache invalidation after reset paths, TC mode setup for 1/4/8 TC configurations, and 32-bit vs 64-bit register access builds.
