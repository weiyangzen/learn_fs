# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_amp_coeff_tables.h

Purpose: provides static Realtek amplifier biquad/BQ coefficient payloads for specific Dell platforms used by `soc_sdw_rt_amp.c`.

Important data: defines `RT1308_MAX_BQ_REG` and `RT1316_MAX_BQ_REG`, then two `static const u8 __maybe_unused` arrays: `dell_0a5d_bq_params[]` and `dell_0b00_bq_params[]`. Each array is a packed byte stream of register address/data triplets or related codec parameter bytes, consumed as a firmware-node `realtek,bq-params` u8 array.

Control flow and state: no executable code. State is compile-time immutable data included into the Realtek amp helper. Runtime copies the relevant array into a stack buffer before creating a software node.

Dependencies and integration: included only by `soc_sdw_rt_amp.c`. DMI matches choose one of these arrays and pass its length via `realtek,bq-params-cnt`.

Risks: values are opaque hardware tuning data; incorrect length or ordering can cause poor audio response or codec misconfiguration. `RT_AMP_MAX_BQ_REG` in the C file is chosen from max register counts and must be large enough for every table. Because arrays are static in a header, including this header from multiple C files would duplicate data.

Test signals: compile-time array size matches DMI platform metadata; runtime codec driver receives the property with expected count; platform audio validation should compare speaker tuning/response on each listed Dell SKU.
