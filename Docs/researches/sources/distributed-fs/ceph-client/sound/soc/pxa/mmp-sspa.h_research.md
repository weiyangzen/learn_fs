# sources/distributed-fs/ceph-client/sound/soc/pxa/mmp-sspa.h

Purpose: defines Marvell MMP SSPA register offsets, bit masks, sample-size encodings, clock-source IDs, and PLL IDs.

Important APIs/types/functions: register offsets include `SSPA_D`, `SSPA_CTL`, `SSPA_SP`, and FIFO/interrupt registers. Macros compose CTL frame/word/sample-size fields and SP enable/reset/frame-sync fields. Clock IDs include `MMP_SSPA_CLK_PLL`, `MMP_SSPA_CLK_VCXO`, `MMP_SSPA_CLK_AUDIO`, `MMP_SYSCLK`, and `MMP_SSPA_CLK`.

Control flow: no runtime flow; the macros are consumed by `mmp-sspa.c` format, clock, and trigger code.

State and persistence: no state, only hardware definitions.

Dependencies and integration: local header for the MMP SSPA DAI driver and any future board-specific users.

Risks: field macros do not mask input values, so callers must pass valid encoded widths. Incorrect bit definitions would break serial port timing and clocking.

Test signals: compile coverage and hardware validation of all supported sample widths and master/slave mode fields.
