# sources/distributed-fs/ceph-client/sound/soc/sof/amd/rembrandt.c

Purpose: Rembrandt DAI capability table and ops initialization.

Important APIs/types/functions: `rembrandt_sof_dai[]` defines HS, BT, SP, DMIC, and HS virtual DAIs with rates/formats/channel constraints. `sof_rembrandt_ops_init()` copies common ACP ops and attaches the DAI array/count.

Control flow: static data is installed during ops init; all runtime callbacks come from common ACP ops.

State and persistence: global `sof_rembrandt_ops` and static DAI definitions.

Dependencies and integration points: paired with `pci-rmb.c`; DAI names must match firmware topology and machine drivers.

Risks: topology/DAI mismatch and stereo-only capture constraints on I2S controllers. Virtual DAI is playback-only.

Test signals: Rembrandt DAI registration, topology graph binding, PCM hw_params negotiation.
