# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/Makefile

## Purpose
The QDSP6 `Makefile` declares how Qualcomm DSP audio support objects are built under Kconfig control. It groups common DSP helpers and AudioReach APM support into composite modules and maps each QDSP6 feature config symbol to the corresponding object.

## Important build APIs and objects
`snd-q6dsp-common-y` links `q6dsp-common.o`, `q6dsp-lpass-ports.o`, and `q6dsp-lpass-clocks.o`. `snd-q6apm-y` links `q6apm.o`, `audioreach.o`, and `topology.o`. Individual `obj-$(CONFIG_...)` lines include Q6 core, AFE, AFE DAI, AFE clocks, ADM, routing, ASM, ASM DAI, APM, APM DAI, APM LPASS DAI, PRM, PRM LPASS clocks, and USB support.

## Control flow and integration
There is no runtime flow, but build-time dependency flow matters. Enabling `CONFIG_SND_SOC_QDSP6_APM` pulls in `audioreach.o` through `snd-q6apm.o`. Enabling `CONFIG_SND_SOC_QDSP6_AFE_DAI` builds `q6afe-dai.o`; enabling `CONFIG_SND_SOC_QDSP6_AFE_CLOCKS` builds `q6afe-clocks.o`; enabling `CONFIG_SND_SOC_QDSP6_ADM` builds `q6adm.o`.

## State and persistence behavior
The file has no runtime state. Its persistent effect is the kernel build graph selected by Kconfig.

## Dependencies and integration points
The Makefile integrates with Linux kbuild and the QDSP6 Kconfig symbols. It defines whether the source files researched in this item are compiled into the kernel for a given configuration.

## Risks and test signals
Risks are missing object dependencies or incorrect composite grouping, which would surface as unresolved symbols or absent drivers at runtime. Test signals include allmodconfig or targeted QDSP6 build coverage, module load availability for AFE/ADM/APM paths, and checking that AudioReach symbols resolve when `CONFIG_SND_SOC_QDSP6_APM` is enabled.
