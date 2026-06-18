<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/disp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/disp.h

## Purpose
Provides R570 RM display control IDs, payload structures, flags, and allocation parameters used by the Nouveau display RM API. It covers static display data, connector and DP capabilities, link rates, active/connect state, backlight control, DP control, stream/audio control, and display channel pushbuffer/channel DMA allocation.

## Important APIs, Types, And Functions
Key APIs/types include NV2080_CTRL_INTERNAL_DISPLAY_GET_STATIC_INFO_PARAMS, NV0073_CTRL_SYSTEM_GET_SUPPORTED_PARAMS, NV0073_CTRL_SPECIFIC_GET_CONNECTOR_DATA_PARAMS, NV0073_CTRL_CMD_DP_GET_CAPS_PARAMS and DSC caps, NV0073_CTRL_SYSTEM_GET_CONNECT_STATE_PARAMS, NV0073_CTRL_DFP_GET_INFO_PARAMS and DFP flag fields, NV0073_CTRL_SYSTEM_GET_ACTIVE_PARAMS, NV0073_CTRL_SPECIFIC_BACKLIGHT_BRIGHTNESS_PARAMS, NV0073_CTRL_CMD_DP_CONFIG_INDEXED_LINK_RATES_PARAMS, NV0073_CTRL_DP_CTRL_PARAMS, NV0073_CTRL_CMD_DP_CONFIG_STREAM_PARAMS, NV0073_CTRL_DP_SET_AUDIO_MUTESTREAM_PARAMS, NV2080_CTRL_INTERNAL_DISPLAY_CHANNEL_PUSHBUFFER_PARAMS, NV50VAIO_CHANNELDMA_ALLOCATION_PARAMETERS, ChannelPBSize, and PBTARGETAPERTURE.

## Control Flow
The header has no executable control flow. Display code issues RM control calls using these command IDs, fills input fields such as subDeviceInstance/displayId/head/sorIndex, and reads output masks, caps, link tables, active display IDs, or error fields. Channel setup uses pushbuffer physical address/limit/aperture/cache fields before allocating DMA display channels.

## State, Persistence, Dependencies, And Integration
State is marshalled in RPC/control payloads and then copied into display/output objects. Dependencies are nvrm/nvtypes.h and bitfield macro conventions. Integration points are nvkm_rm_api_disp hooks, DP AUX/I2C output probing, display channel allocation, backlight operations, and modeset/link-training code that needs RM DP caps.

## Risks And Test Signals
Risks: duplicate DP_GET_CAPS define is harmless but shows imported-header fragility; bitfield values must match RM exactly; display hotplug/backlight/link-rate behavior depends on firmware interpreting these payloads. Test signals include display enumeration masks, connector data retrieval, DP caps/link-rate configuration, active-head queries, backlight get/set, and display channel pushbuffer allocation on R570 firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r570/nvrm/disp.h -->
