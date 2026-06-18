# sources/distributed-fs/ceph-client/drivers/reset/tegra/reset-bpmp.c

Purpose: Tegra BPMP reset-controller implementation that forwards reset requests to BPMP firmware using MRQ_RESET messages.

Important APIs/types/functions: `tegra_bpmp_reset_common()` builds `mrq_reset_request` and `tegra_bpmp_message`, calls `tegra_bpmp_transfer()`, and maps BPMP return values. `.reset`, `.assert`, and `.deassert` wrap BPMP commands. `tegra_bpmp_init_resets()` fills the embedded `bpmp->rstc` and registers it.

Control flow: BPMP core initializes reset support after it knows `soc->num_resets`. Consumers call reset ops, which synchronously send firmware messages.

State and persistence: controller is embedded in `struct tegra_bpmp`; firmware owns hardware reset state.

Dependencies and integration: Tegra BPMP core, BPMP ABI, reset-controller framework.

Risks and test signals: any nonzero BPMP message return becomes `-EINVAL`, losing detailed firmware errors. Test firmware transfer failures, invalid reset IDs, all three commands, and `num_resets` correctness for each SoC.
