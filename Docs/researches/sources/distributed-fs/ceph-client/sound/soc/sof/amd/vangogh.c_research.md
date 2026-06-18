# sources/distributed-fs/ceph-client/sound/soc/sof/amd/vangogh.c

Purpose: Vangogh DAI capability table and platform-specific ops tweaks for quirked firmware behavior.

Important APIs/types/functions: `vangogh_sof_dai[]` defines HS, BT, SP, DMIC, and HS virtual DAIs. `sof_vangogh_post_fw_run_delay()` delays after resume boot for quirked systems. `sof_vangogh_ops_init()` copies common ops, installs DAIs, and applies DMI quirk overrides for signed firmware loading and post-run delay.

Control flow: ops init checks `acp_sof_quirk_table`; signed firmware switches `.load_firmware` to `acp_sof_load_signed_firmware`, and post-run quirk sets `.post_fw_run`. Delay only runs when `!sdev->first_boot`.

State and persistence: global `sof_vangogh_ops`; quirk decisions are reflected in function pointers.

Dependencies and integration points: `pci-vangogh.c` descriptor, common ACP loader, DMI quirk table in `acp.c`, SOF core firmware run sequence.

Risks: DMI matching controls critical firmware path changes. Delay workaround is timing-sensitive and only applied after first boot.

Test signals: Vangogh boot/resume on quirked and non-quirked devices, signed firmware code/data file requests, and DAI topology binding.
