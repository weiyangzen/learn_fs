# sources/distributed-fs/ceph-client/sound/soc/sof/amd/renoir.c

Purpose: Renoir DAI capability table and ops initialization.

Important APIs/types/functions: `renoir_sof_dai[]` defines BT, SP, DMIC, and SP virtual DAI entries. `sof_renoir_ops_init()` clones `sof_acp_common_ops` and sets `.drv`/`.num_drv`.

Control flow: ops init installs static DAIs; common ACP code handles all hardware behavior.

State and persistence: global `sof_renoir_ops` and static DAI table.

Dependencies and integration points: used by `pci-rn.c`, ASoC component registration, SOF topology DAI matching.

Risks: no HS DAI on Renoir. Capture constraints differ from playback; incorrect topology channel/rate assumptions fail negotiation.

Test signals: Renoir topology loading, DAI names `acp-sof-bt`, `acp-sof-sp`, `acp-sof-dmic`, and PCM parameter tests.
