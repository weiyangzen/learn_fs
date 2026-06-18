<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/i2s_test.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/i2s_test.c

Purpose: test/loopback machine driver for manually selected AVS SSP/TDM I2S paths.

Important APIs, types, and functions: platform driver `avs_i2s_test`; `avs_i2s_test_probe()`; `avs_create_dai_link()`.

Control flow: board selection parses the `i2s_test=` module parameter, creates one platform device per selected SSP/TDM slot, and sets topology names like `i2s<ssp>[:tdm]-test-tplg.bin`. Probe validates exactly one SSP and one TDM slot, creates a single no-PCM backend link with a dummy codec, chooses either legacy loopback naming or modern "AVS I2S TEST-..." naming, and registers the card.

State and persistence: no persistent private state. The selected SSP/TDM mask is carried in `avs_mach_pdata.tdms` and `mach_params.i2s_link_mask`.

Dependencies and integration points: depends on `avs_register_i2s_component()` CPU DAI creation and firmware/topology support for loopback test paths. It intentionally uses `snd_soc_dummy_dlc` instead of a real codec.

Risks: this bypasses ACPI codec matching, so invalid module parameters can create cards that topology or hardware cannot use. It rejects multi-SSP/multi-TDM cards, matching the one-link implementation.

Test signals: passing `i2s_test=...` creates loopback cards, dummy codec links bind, invalid multi-slot data returns `-EINVAL`, and test topology files load for the requested SSP/TDM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/i2s_test.c -->
