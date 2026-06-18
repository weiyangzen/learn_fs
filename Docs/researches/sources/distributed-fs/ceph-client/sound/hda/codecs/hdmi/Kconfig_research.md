# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/Kconfig

## Purpose
Defines the Kconfig menu for HD-audio HDMI and DisplayPort codec support. It lets the common HDMI support and vendor-specific HDMI codec drivers be built in, built as modules, or disabled, with individual controls visible to expert configurations.

## Important APIs, Types, and Functions
This is configuration metadata rather than C code. The top-level `SND_HDA_CODEC_HDMI` `menuconfig` gates all HDMI/DP codec choices. Sub-options include `SND_HDA_CODEC_HDMI_GENERIC`, `SND_HDA_CODEC_HDMI_SIMPLE`, `SND_HDA_CODEC_HDMI_INTEL`, `SND_HDA_INTEL_HDMI_SILENT_STREAM`, `SND_HDA_CODEC_HDMI_ATI`, `SND_HDA_CODEC_HDMI_NVIDIA`, `SND_HDA_CODEC_HDMI_NVIDIA_MCP`, and `SND_HDA_CODEC_HDMI_TEGRA`.

## Control Flow
When HDMI support is selected, the generic and vendor codec options default to `y`; under `CONFIG_EXPERT`, users can tune them individually. Intel, AMD/ATI, Nvidia, and Tegra options select the generic HDMI codec support where they extend the generic implementation. Legacy Nvidia MCP selects the simpler HDMI support. Intel silent stream is a bool that depends on Intel HDMI support and enables keep-alive/silent-stream behavior on capable hardware.

## State and Persistence Behavior
Kconfig choices persist in the kernel `.config` and drive compilation and module availability. They do not create runtime state directly, but their selected symbols decide which objects and feature code enter the build.

## Dependencies and Integration Points
`SND_HDA_CODEC_HDMI_GENERIC` selects `SND_DYNAMIC_MINORS` for DP-MST multi-stream minor allocation and `SND_PCM_ELD` for ELD parsing/support. Vendor options select generic or simple HDMI support and are consumed by the HDMI `Makefile` to build the corresponding modules. The options integrate with ALSA HDA codec registration and GPU audio component behavior once compiled.

## Risks
The top-level option text contains a typo, "DislayPort", but behavior is unaffected. Functional risk is mainly dependency drift: failing to select `SND_DYNAMIC_MINORS`, `SND_PCM_ELD`, or the right generic/simple base would produce missing symbols or incomplete DP-MST/ELD behavior. Defaults to `y` under the parent can increase build surface unless expert users disable drivers.

## Test Signals
Kconfig tests should verify valid `y`, `m`, and `n` combinations; dependency propagation for generic, Intel, AMD/ATI, Nvidia, Nvidia MCP, and Tegra; successful builds for modular and built-in configurations; and presence or absence of the expected `snd-hda-codec-*` modules matching the selected symbols.
