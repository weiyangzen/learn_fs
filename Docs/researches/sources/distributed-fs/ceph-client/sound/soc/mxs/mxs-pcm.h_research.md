# sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-pcm.h

Purpose: declares the MXS PCM platform registration helper.

Important APIs/types/functions: `mxs_pcm_platform_register(struct device *dev)` is the only exported API.

Control flow: no runtime flow; `mxs-saif.c` includes this header and calls the helper during probe.

State and persistence: no state.

Dependencies and integration: keeps the SAIF driver independent from the PCM helper implementation while allowing modular symbol export.

Risks: signature drift would break the SAIF build. The header does not include `struct device` forward declaration, relying on including files to provide it.

Test signals: compile and modpost coverage for MXS SAIF plus PCM objects.
