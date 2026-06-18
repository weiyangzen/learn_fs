# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/ahb.h

## Purpose
`ahb.h` defines the private AHB transport state used by `ahb.c` and constants for recovery and SMP2P power-save messages. It is the small contract that lets the generic `ath11k_base` carry AHB-specific remoteproc, firmware memory, and SMEM state without exposing those fields to unrelated transports.

## Important APIs, Types, And Functions
`ATH11K_AHB_RECOVERY_TIMEOUT` bounds removal waits while firmware recovery is active. `ATH11K_AHB_SMP2P_SMEM_MSG`, `ATH11K_AHB_SMP2P_SMEM_SEQ_NO`, and `ATH11K_AHB_SMP2P_SMEM_VALUE_MASK` describe the packed SMEM state value used to enter and exit power save. `enum ath11k_ahb_smp2p_msg_id` provides the `ATH11K_AHB_POWER_SAVE_ENTER` and `ATH11K_AHB_POWER_SAVE_EXIT` command IDs. `struct ath11k_ahb` stores `tgt_rproc`, firmware memory/IOMMU state, and SMP2P state. `ath11k_ahb_priv()` casts `ab->drv_priv` to the AHB private structure.

## Control Flow
The header itself has no runtime flow, but its fields are filled during `ath11k_ahb_probe()` resource setup, consumed during remoteproc power up/down, used by fixed firmware-memory initialization/deinitialization, and updated during WCN6750 HIF suspend/resume when SMP2P messages are sent.

## State And Persistence
All state is in-memory for the device lifetime. The nested `fw` state tracks whether firmware memory is controlled through TrustZone (`use_tz`) or a local IOMMU domain, plus MSA and CE physical regions. The nested `smp2p_info` carries an incrementing sequence number, SMEM bit, and `qcom_smem_state` handle.

## Dependencies And Integration Points
The header includes `core.h`, so it depends on the main ath11k object model and Linux types brought in through core. Its contents are used only by the AHB platform implementation and indirectly by HIF power-management hooks.

## Risks And Test Signals
The key risk is that this private layout must match the `priv_size` passed to `ath11k_core_alloc()` in `ahb.c`; misuse would corrupt driver-private state. SMP2P bit packing must remain consistent with firmware expectations. Test signals are successful AHB probe/remove, WoW suspend/resume SMEM messages, and fixed-memory firmware boot on platforms with `wifi-firmware` nodes.
