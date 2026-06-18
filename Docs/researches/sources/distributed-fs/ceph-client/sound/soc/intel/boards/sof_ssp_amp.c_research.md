# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_ssp_amp.c

Purpose: SOF machine driver for Intel designs centered on SSP-connected speaker amplifiers, including RT1308 and CS35L41, with optional HDMI capture, HDMI playback, DMIC, and BT offload.

Important APIs, types, and functions: Quirk bit `SOF_HDMI_PLAYBACK_PRESENT` controls iDisp HDMI playback. `SSP_AMP_LINK_ORDER` and `SSP_AMP_LINK_IDS` define topology-compatible ordering and fixed BE ids for HDMI-in capable topologies. `sof_card_dai_links_create()` uses the common board helper and patches the amp link for CS35L41 or RT1308. `sof_ssp_amp_probe()` applies platform id quirks, disables PCH DMIC on non-Chromebook systems with no ACPI DMIC count, controls HDMI playback presence, installs fixed ids when HDMI-in SSP mask is present, updates codec_conf, fixes platform names, and registers the card.

Control flow and integration: The driver is a policy wrapper around `sof_board_helpers.c` and amplifier helper modules. Platform ids describe generic amp-only systems, RT1308 HDMI-in systems, CS35L41 systems, and LT6911 HDMI capture designs across Intel generations.

State and persistence: Module-global quirk and devm `sof_card_private`. Static card data. No persistent storage.

Dependencies: SOF board helpers, Realtek and Cirrus amp helpers, DMI Chromebook detection, ACPI mach params, ASoC PM ops.

Risks: Fixed BE ids must match topology files. DMIC suppression policy differs for Chromebooks. HDMI-in masks can create multiple capture SSP links. Test signals include RT1308 and CS35L41 playback, HDMI capture on specified SSP ports, HDMI playback presence/absence, BT offload, DMIC policy, and card component prefixes for CS35L41.
