# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-interconnection.h

This header defines numeric AFE interconnection input-port ids used by DAPM mixer controls throughout the MT8192 audio driver. The first group defines direct input ports below 32 for I2S0, ADDA uplink, DL1/DL2/DL12/DL3, PCM capture, gain outputs, ADDA CH34, and I2S2 channels. The second group defines hardware values at or above 32 by subtracting `I_32_OFFSET`, covering CONNSYS I2S, SRC outputs, DL4-DL9, I2S6, and I2S8.

ADDA, I2S, PCM, and memif DAPM mixer controls use these macros as shift positions in `SOC_DAPM_SINGLE_AUTODISABLE()` against `AFE_CONN*` or `AFE_CONN*_1` registers. The split at 32 matches the hardware register-bank split in the connection registers.

There is no runtime state. The main dependency is callers selecting the correct connection register bank for each macro. A mismatch between label, port macro, and register bank silently creates wrong audio routes. Test signals are route-level loopback or board audio tests that activate every DAPM mixer source, especially the >=32 ports that require `_1` registers.
