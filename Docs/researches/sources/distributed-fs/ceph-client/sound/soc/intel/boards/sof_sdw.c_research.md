# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_sdw.c

Purpose: Generic SOF SoundWire machine driver for Intel platforms. It dynamically creates DAI links from ACPI SoundWire endpoint descriptions and augments them with SSP, PCH DMIC, iDisp HDMI, BT offload, and echo-reference links.

Important APIs, types, and functions: Module/DMI/SSID quirks encode jack source, HDMI generation, PCH DMIC, SSP ports, BT offload, sidecar amps, codec speaker/mic policy, and deprecated flags. `create_sdw_dailink()` creates playback/capture links per parsed SoundWire dailink, builds CPU pins and codec components, fills channel maps, adds codec_conf prefixes and sidecar devices, and invokes codec-specific init callbacks. `create_sdw_dailinks()`, `create_ssp_dailinks()`, `create_dmic_dailinks()`, `create_hdmi_dailinks()`, `create_bt_dailinks()`, and `create_echoref_dailink()` synthesize all BE classes. `sof_card_dai_links_create()` parses endpoints through SoundWire utility APIs, counts links/configs/aux devices, allocates card arrays, and builds the full topology. `mc_probe()` builds the card context, applies quirks, resets amp counters, registers the card, and wires cleanup.

Control flow and integration: Probe sets up `asoc_sdw_mc_private` with an Intel-private context, applies PCI SSID and DMI quirks, then delegates to dynamic link creation. Late probe runs generic SoundWire late-probe and HDMI control setup. `add_dai_link` ignores HDMI FE PCMs when iDisp is absent. Remove calls the SoundWire dailink exit loop.

State and persistence: State includes module-global `sof_sdw_quirk`, card context, Intel HDMI/pin-index state, dynamically allocated parsed endpoint arrays freed before return, and devm-managed card arrays. No disk persistence.

Dependencies: `sound/soc_sdw_utils`, SoundWire ACPI metadata, HDA DSP HDMI helper, ASoC, DMI/PCI quirk tables, RT711 jack quirk constants, and SOF topologies expecting generated BE ids.

Risks: This file has a large and evolving quirk matrix. Deprecated quirks log errors but do not implement old behavior. Endpoint parsing and BE id assignment must match topology expectations. HDMI link count is always added to link allocation even if iDisp is absent, with FE ignore used later. Test signals include endpoint parsing on all supported codec mixes, sidecar amp/mic policies, PCH versus SDW DMIC conflict warnings, HDMI controls, BT offload, echo reference link presence, amp count component strings, and cleanup on registration failure/remove.
