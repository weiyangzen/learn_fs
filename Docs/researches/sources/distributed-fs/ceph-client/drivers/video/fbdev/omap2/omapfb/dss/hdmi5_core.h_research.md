# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi5_core.h

## Purpose
`hdmi5_core.h` is the HDMI5 core contract for OMAP5/DRA7. It enumerates the register map for identification, interrupt handling, video sampler, video packetizer, frame composer, audio, main controller, CSC, HDCP/CEC masks, and I2C-master DDC, plus the small structs and function prototypes used by `hdmi5_core.c`.

## Important APIs, types, and functions
Important definitions include `HDMI_CORE_IH_*`, `HDMI_CORE_TX_*`, `HDMI_CORE_VP_*`, `HDMI_CORE_FC_*`, `HDMI_CORE_AUD_*`, `HDMI_CORE_MC_*`, `HDMI_CORE_CSC_*`, and `HDMI_CORE_I2CM_*`. `enum hdmi_core_packet_mode` defines pixel packet modes. `struct hdmi_core_vid_config` carries derived frame-composer state, and `struct csc_table` carries twelve coefficients. Prototypes expose EDID, dump, video configure, init, and audio configure routines.

## Control Flow
The header has no executable flow. Its register and type definitions support the control flow in `hdmi5_core.c`: DDC uses the I2CM offsets, video setup uses FC/VP/TX/CSC/MC offsets, audio uses AUD and FC audio offsets, and interrupt masking uses IH and mask registers.

## State and Persistence
No state is stored in the header. It describes register-resident state retained by the HDMI core until reset or reprogramming. The macros for indexed payload/channel registers define how variable register arrays are addressed.

## Dependencies and Integration Points
It includes the shared `hdmi.h` API, making common wrapper structures available to HDMI5 core code. It is consumed by `hdmi5_core.c` and indirectly by `hdmi5.c` through the exported prototypes.

## Risks
Because this is a dense hardware register header, risks are incorrect offsets, bit-width assumptions, and mismatch with the HDMI IP revision. The `HDMI_CORE_I2CM_DATAI` define uses uppercase `0X`, which compiles but is visually inconsistent. Feature expansion for HDCP/CEC or deep color would need coordinated additions here and in the core implementation.

## Test Signals
Compile coverage, register dump sanity against TRM values, EDID/DDC operation, HDMI5 video bring-up, audio register programming, and analyzer-observed infoframe/audio packets are the practical validation signals.
