# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dprtc.h

Purpose: Public local header for the DPAA2 Data Path Real Time Counter API. It exposes the DPRTC interrupt constants and the MC command wrapper prototypes implemented in `dprtc.c`.

Important APIs and types: Defines `DPRTC_MAX_IRQ_NUM` as one IRQ and `DPRTC_IRQ_INDEX` as index zero. Event bit definitions include `DPRTC_EVENT_PPS`, `DPRTC_EVENT_ETS1`, and `DPRTC_EVENT_ETS2`. Function declarations cover session lifecycle and IRQ enable/mask/status/clear operations, all parameterized by `struct fsl_mc_io`, command flags, token, and IRQ index.

Control flow and state: The header has no executable control flow. It defines the contract that consumers follow: open an object to get a token, perform interrupt operations using that token, then close the session.

Dependencies and integration points: Forward-declares `struct fsl_mc_io` and expects Linux integer typedefs to be available from includers. It is included by `dprtc.c` and by DPAA2 drivers that need access to RTC/PPS/ETS events through the MC.

Risks: There is only one IRQ index; callers using arbitrary indexes may receive firmware errors. Event bit constants must match firmware event causes. Since the header exposes raw `u32` masks rather than typed flags, accidental mixing with other DPAA2 event masks is possible.

Test signals: Compile-time coverage for users of the prototypes, runtime validation of event masks against actual PPS/ETS interrupt generation, and negative tests for invalid tokens or IRQ indexes.
