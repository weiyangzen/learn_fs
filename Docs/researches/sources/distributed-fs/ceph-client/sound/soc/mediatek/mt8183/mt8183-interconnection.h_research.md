# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-interconnection.h

Purpose: defines numeric interconnection input indices used by MT8183 DAPM mixer controls to connect AFE sources to sinks through `AFE_CONN*` registers.

Important APIs/types/functions: provides `#define` constants for I2S channels, ADDA UL channels, DL1/DL2/DL3 channels, PCM capture channels, and gain outputs. These constants are used as bit positions in `SOC_DAPM_SINGLE_AUTODISABLE` controls across ADDA, I2S, PCM, and memif DAI files.

Control flow: no executable code. At compile time, DAI files include the constants and bake them into DAPM mixer controls; at runtime, DAPM toggles the associated AFE connection register bits.

State and persistence: no state in the header; the effective state is the hardware connection matrix bits controlled by the generated DAPM controls.

Dependencies and integration: tied to MT8183 AFE hardware register layout and `mt8183-reg.h` connection register addresses. Every DAI route using these values depends on the numeric definitions matching the SoC interconnect matrix.

Risks: wrong bit positions silently route audio incorrectly. The sparse numbering makes copy/paste mistakes likely when adding routes. There is no compile-time validation against the register field definitions.

Test signals: route-level audio tests for each source/sink combination, DAPM register tracing for `AFE_CONN*`, and comparing constants against vendor register documentation.
