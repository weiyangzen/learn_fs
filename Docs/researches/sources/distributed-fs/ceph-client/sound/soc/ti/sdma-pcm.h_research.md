<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/sdma-pcm.h -->
# sources/distributed-fs/ceph-client/sound/soc/ti/sdma-pcm.h

## Purpose
Small public helper header for TI sDMA PCM platform registration.

## APIs, Types, and Functions
Declares `sdma_pcm_platform_register()` when `CONFIG_SND_SOC_TI_SDMA_PCM` is enabled. Otherwise provides a stub returning `-ENODEV`.

## Control Flow, State, and Persistence
The header has no runtime state. It controls compile-time integration: drivers can call the helper unconditionally and receive an explicit failure when the helper is not built.

## Dependencies and Integration
Used by TI OMAP audio CPU DAI/glue drivers that depend on sDMA. Its behavior affects whether those drivers can successfully probe when the sDMA PCM module is disabled.

## Risks and Test Signals
Risk is probe failure for callers that require sDMA but do not select the config, since the stub returns `-ENODEV`. Test signals are builds with helper enabled/disabled and probe behavior for McBSP, McPDM, DMIC, and HDMI callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/sdma-pcm.h -->
