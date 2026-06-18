# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp70.c

Purpose: ACP7.0/7.1 platform DAI declarations and ops initialization.

Important APIs/types/functions: `acp70_sof_dai[]` defines HS, BT, SP, DMIC, and HS virtual DAIs. `sof_acp70_ops` is exported, and `sof_acp70_ops_init()` clones common ACP ops and supplies platform DAI drivers.

Control flow: same pattern as ACP63: static DAI capability table plus init-time ops template copy.

State and persistence: global ops table and static DAI array.

Dependencies and integration points: used by `pci-acp70.c` for ACP70/71/72 revisions. Relies on common ACP code for all hardware behavior.

Risks: same DAI/topology mismatch risks as ACP63. ACP70 hardware differences are mostly handled in descriptors/common code, so this file must stay aligned with those descriptor capabilities.

Test signals: ACP70/71/72 DAI registration, topology match, and PCM negotiation.
