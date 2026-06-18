<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/board_selection.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/board_selection.c

Purpose: AVS board enumeration for the Intel cAVS/AVS PCI driver. It translates detected firmware/hardware capabilities, NHLT endpoints, ACPI codec IDs, DMI quirks, HDA codec discovery, and module parameters into platform devices for ASoC machine drivers and AVS CPU components.

Important APIs, types, and data: exports `avs_register_all_boards()` and `avs_unregister_all_boards()`. The file builds arrays of `struct snd_soc_acpi_mach` for SKL/KBL/APL/GLK/CNL/ICL/TGL/MBL-class platforms, using `.id`, `.uid`, `.drv_name`, `.mach_params.i2s_link_mask`, optional `.machine_quirk`, optional `.pdata` TDM masks, and topology filenames. `struct avs_acpi_boards` maps PCI device IDs to those arrays. Module parameters are `i2s_test` and `obsolete_card_names`; the latter is copied into `struct avs_mach_pdata`.

Control flow: `avs_register_all_boards()` conditionally registers a probe board when debugfs is enabled, then DMIC, I2S test boards from the module parameter, ACPI/NHLT-driven I2S boards, and finally one HDAudio board per probed HDA codec. `avs_register_board()` uses `platform_device_register_data()` and registers a devm cleanup action so platform devices are removed with the AVS PCI device. `avs_register_board_pdata()` allocates AVS-specific platform data, attaches codec/TDM/card-name metadata to the ACPI machine descriptor, and passes a copied machine object as platform data to the board driver.

State and persistence: board platform devices are transient kernel devices tied to the AVS device lifetime by devm actions. `mach->pdata` is mutated before registration, so static `snd_soc_acpi_mach` entries are shared state; this is acceptable for a single AVS controller path but worth noticing for re-probe and concurrent assumptions. Firmware topology filename selection is persisted in the platform data consumed by later ASoC registration.

Dependencies and integration points: depends on ACPI NHLT (`acpi_nhlt_find_endpoint()`), ACPI codec presence (`acpi_dev_present()`), HDA codec lists, DMI matching, `avs_register_*_component()` from the PCM/probe layers, and board modules with platform names such as `avs_rt286`, `avs_dmic`, and `avs_hdaudio`. Topology names must match firmware topology files and backend DAI names used by board drivers.

Risks: stale or missing ACPI/DMI entries can select the wrong codec driver or topology. `i2s_test` parsing allocates an integer array and rejects more SSPs than hardware reports, but invalid TDM masks can still create multiple loopback boards. Several static machine entries carry compound-literal pdata/TDM arrays, so lifetime is static but mutation of `.pdata` later can obscure original defaults. HDA/DMIC/I2S registration warns but generally continues, so partial cards are expected on mixed endpoint systems.

Test signals: boot logs for "enumerate ... endpoints failed", visible platform devices/cards for each endpoint, topology filename loading, `i2s_test=` loopback card creation, DMI-specific KBL/KBL-R RT286/RT298 selection, and ACPI NHLT systems with no endpoints returning quietly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/board_selection.c -->
