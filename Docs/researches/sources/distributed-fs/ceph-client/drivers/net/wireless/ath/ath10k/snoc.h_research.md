# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/snoc.h

Purpose: Declares SNOC-specific private structures, flags, and public hooks used by the WCN3990 platform transport.

Important APIs and types: Defines `ath10k_snoc_drv_priv`, `snoc_state`, `ath10k_snoc_pipe`, `ath10k_snoc_target_info`, `ath10k_snoc_ce_irq`, `enum ath10k_snoc_flags`, `struct ath10k_snoc`, `ath10k_snoc_priv()`, `ath10k_snoc_fw_indication()`, and `ath10k_snoc_fw_crashed_dump()`.

Control flow, state, and persistence: No executable control flow besides the private accessor. The structures describe persistent driver runtime state: CE pipe metadata and locks, firmware DMA/IOMMU mapping, MMIO memory, power resources, QMI client, SSR notifier, recovery flags, and pending CE IRQ bitmap.

Dependencies and integration points: Includes ath10k hardware, CE, and QMI headers plus Linux notifier types. It is shared between `snoc.c` and QMI/firmware notification paths.

Risks: Flag meanings (`REGISTERED`, `UNREGISTERING`, `MODEM_STOPPED`, `RECOVERY`, host-cap quirks) are cross-module coordination points; stale flag updates can cause double registration, skipped recovery, or incorrect WLAN disable. Pipe state embeds both CE and ath10k pointers, so teardown order matters.

Test signals: Compile SNOC builds, exercise firmware ready/down callbacks, CE pipe setup and cleanup, quirk parsing, and crash dump invocation through QMI/recovery paths.
