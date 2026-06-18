# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/targaddrs.h

Purpose: Defines target RAM host-interest addresses, the packed `host_interest` shared ABI, host-interest item offset macro, option/reset/ACS/power-save/WOW/SMPS bitfields, and board-data size constants for ath10k firmware coordination.

Important APIs and definitions: Key exports include `QCA988X_HOST_INTEREST_ADDRESS`, `HOST_INTEREST_MAX_SIZE`, `struct host_interest`, `HI_ITEM()`, host option bits, firmware mode/submode masks, SDIO ACS flags, SDIO crash dump enhancement flags, reset flags, console flags, WOW extension encode/decode macros, early allocation macros, power-save/SMPS macros, and board/ext-board data sizes for QCA988x/QCA6174/QCA9377/QCA99x0/QCA4019/WCN3990.

Control flow, state, and persistence: This header has no runtime flow. The structure layout and offsets are persistent firmware ABI: comments state fields must remain at fixed positions and additions belong at the end. Drivers access values through BMI or diagnostic windows during boot, SDIO start-post, crashdump, board-data upload, and feature negotiation.

Dependencies and integration points: Includes `hw.h` for target hardware definitions. It is used by SDIO, BMI/core firmware loading, board data setup, crash dumping, and host-interest feature/quirk negotiation.

Risks: Reordering or resizing `struct host_interest` breaks firmware compatibility. Some utility macros reference `HOST_INTEREST`, implying target-side use as well as host-side C use. Board-data constants must match firmware expectations. Misreading SDIO ACS or crashdump flags can route traffic to the wrong mailbox or choose an unsupported dump path.

Test signals: Boot each supported hardware family, board-data upload size checks, SDIO mailbox swap and reduced TX-completion acknowledgement, crashdump fast-dump negotiation, WOW/SMPS option programming, and compatibility with firmware revisions that add host-interest fields.
