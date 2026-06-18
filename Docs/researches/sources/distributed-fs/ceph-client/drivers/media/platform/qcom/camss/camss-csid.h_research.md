# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid.h

## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid.h

Purpose: Public internal header for the Qualcomm CAMSS CSID module, defining pad layout, testgen modes, format metadata, PHY config, hardware operation callbacks, CSID resource descriptors, and common function prototypes.

Important APIs/types/functions: Defines `MSM_CSID_PAD_SINK`, `MSM_CSID_PAD_FIRST_SRC`, `MSM_CSID_PADS_NUM`, `MSM_CSID_MAX_SRC_STREAMS`, `CSID_RESET_TIMEOUT_MS`, `enum csid_testgen_mode`, `struct csid_format_info`, `struct csid_formats`, `struct csid_testgen_config`, `struct csid_phy_config`, `struct csid_hw_ops`, `struct csid_subdev_resources`, and `struct csid_device`. Declares common helpers and external ops for 4.1, 4.7, 340, 680, Gen2, and Gen3.

Control flow/state: The central persistent state is `struct csid_device`: CAMSS pointer, id, subdev/pads, MMIO base, IRQ, clocks/regulators, reset completion, testgen control state, PHY lane/VC state, per-pad formats, controls, and hardware resource pointer. `struct csid_hw_ops` is the polymorphic dispatch table used by the common core for stream config, reset, ISR, version read, source-code negotiation, subdev init, and optional register updates.

Dependencies/integration: Includes Linux clock/interrupt and media/V4L2 subdev/control headers. It is included by common and generation-specific CAMSS CSID files and by `camss.h`.

Risks/test signals: Header changes affect every CSID generation. Risks include callback contract mismatches, pad-count assumptions, and VC/source-pad indexing errors. Test by compiling all CAMSS variants and running media graph link/stream paths for single and multiple RDI source pads.
