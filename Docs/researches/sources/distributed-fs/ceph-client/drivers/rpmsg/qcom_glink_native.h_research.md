# sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_native.h

Purpose: public internal interface between Qualcomm GLINK native core and concrete GLINK pipe transports.

Important APIs/types/functions: feature bits include `GLINK_FEATURE_INTENT_REUSE`, `GLINK_FEATURE_MIGRATION`, and `GLINK_FEATURE_TRACER_PKT`. `struct qcom_glink_pipe` abstracts FIFO length and callbacks for availability, peek, advance, write, and kick. Exports `qcom_glink_native_probe()`, `qcom_glink_native_remove()`, and `qcom_glink_native_rx()`.

Control flow: transport drivers provide RX/TX pipe implementations and call probe to create a GLINK edge, call RX when data arrives, and call remove during teardown.

State and persistence: header declares opaque `struct qcom_glink`; actual state is private to `qcom_glink_native.c`.

Dependencies and integration: uses Linux types and device forward declarations; consumed by GLINK SMEM/RPM-style transports.

Risks and test signals: pipe callback contracts are critical; wrong `avail`, alignment, or `advance` behavior corrupts protocol parsing. Test with each pipe backend, RX/TX wraparound, zero/large messages, and teardown ordering.
