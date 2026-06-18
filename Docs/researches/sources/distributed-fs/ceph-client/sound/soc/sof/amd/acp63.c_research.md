# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp63.c

Purpose: ACP6.3 platform DAI declarations and ops initialization.

Important APIs/types/functions: `acp63_sof_dai[]` defines HS, BT, SP, DMIC, and HS virtual DAIs with playback/capture capabilities. `sof_acp63_ops` is exported, and `sof_acp63_ops_init()` copies `sof_acp_common_ops` then attaches the DAI array/count.

Control flow: ops init is called by the SOF core through the PCI descriptor before probe validation. No runtime logic beyond copying the common ops template.

State and persistence: global `sof_acp63_ops` persists as the platform ops table. DAI capabilities are static.

Dependencies and integration points: paired with `pci-acp63.c`, common ACP ops, and ASoC DAI registration in the SOF core.

Risks: DAI capability mismatches with firmware topology or machine drivers cause PCM open/hw_params failures. Capture on I2S DAIs is intentionally limited to stereo.

Test signals: ACP63 probe, DAI registration, topology binding to `acp-sof-*` DAI names, and PCM parameter negotiation.
