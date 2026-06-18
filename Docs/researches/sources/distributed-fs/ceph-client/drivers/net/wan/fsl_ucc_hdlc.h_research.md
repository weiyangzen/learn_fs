# sources/distributed-fs/ceph-client/drivers/net/wan/fsl_ucc_hdlc.h

Purpose: private definitions for the Freescale QUICC Engine UCC HDLC driver. It captures the hardware parameter RAM layout, driver-private runtime state, ring sizes, buffer sizing, CRC defaults, address/header constants, and event masks.

Important APIs, types, and functions: `struct ucc_hdlc_param` mirrors UCC HDLC parameter RAM fields in big-endian hardware order. `struct ucc_hdlc_private` carries UCC/TDM handles, netdev, NAPI, register pointers, DMA buffers, BD rings, SKB arrays, ring indices, configuration flags, locks, and PM backup state. Macros include `UCCE_HDLC_RX_EVENTS`, `UCCE_HDLC_TX_EVENTS`, `TX_BD_RING_LEN`, `RX_BD_RING_LEN`, `MAX_RX_BUF_LENGTH`, `MAX_FRAME_LENGTH`, `HDLC_HEAD_LEN`, `HDLC_CRC_SIZE`, `CRC_16BIT_MASK`, and default HDLC/PPP address/header constants.

Control flow: no executable flow. The C file uses these definitions to allocate rings, program parameter RAM, classify interrupt events, prepend/strip headers, compute ring wrap masks, and restore PM state.

State and persistence: defines in-memory and MURAM state structures only. Hardware register/parameter contents persist only while the device is powered or until reinitialized.

Dependencies and integration points: includes QUICC Engine headers for `ucc_fast`, `ucc_tdm`, `qe_bd`, and register definitions. The netdev/HDLC-facing state is intentionally private to `fsl_ucc_hdlc.c`.

Risks: ring modulo macros assume power-of-two ring sizes. `struct ucc_hdlc_param` layout must exactly match hardware. Fixed buffer sizes constrain max frame behavior. PM backup fields are compiled only with `CONFIG_PM`, so non-PM code must not touch them.

Test signals: structure offset/size review against QE documentation, ring wrap tests, max-frame tests, CRC/header behavior for raw and PPP modes, and PM builds with and without `CONFIG_PM`.
