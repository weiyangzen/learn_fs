# sources/distributed-fs/ceph-client/drivers/media/i2c/ths8200_regs.h

Purpose: Provides symbolic register offsets for the THS8200 video encoder. It is the register-map contract consumed by `ths8200.c`.

Important APIs, types, and functions: There are no functions or data types. The header defines offsets for chip control/version, color-space conversion coefficients, data control, display timing generator groups DTG1 and DTG2, DAC controls, clipping/scaling/matrix registers, CGMS registers, and miscellaneous pixel-per-line/filter controls.

Control flow: None. Runtime code uses the macros as addresses passed to SMBus byte-data read/write helpers.

State and persistence: None in the header. Each macro corresponds to a hardware register whose state is managed by the encoder.

Dependencies and integration points: Included by `ths8200.c`. The offsets are tightly coupled to helper code that performs read/modify/write on bit-packed fields, especially combined MSB registers such as `THS8200_DTG1_SPEC_DEH_MSB`, `THS8200_DTG2_HLENGTH_LSB_HDLY_MSB`, and `THS8200_DTG2_VLENGTH1_MSB_VDLY1_MSB`.

Risks: The header contains a duplicate `THS8200_CSM_MULT_RCR_LSB` define at the same value, harmless for compilation but a maintenance smell. It only names offsets, not masks or shifts, so call sites must hand-code bit operations and are vulnerable to field-packing mistakes. No comments document valid bit values beyond broad grouping.

Test signals: Build coverage catches missing include guards or macro spelling. Higher-value tests are generated register-write traces from `ths8200.c`, since this header's correctness is validated by using the offsets to program a known timing and comparing against the THS8200 datasheet.
