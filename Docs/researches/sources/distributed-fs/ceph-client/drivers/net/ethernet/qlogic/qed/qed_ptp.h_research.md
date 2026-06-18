# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ptp.h

Purpose: Declares the QED Ethernet PTP operations table exported by `qed_ptp.c`.

Important APIs/types/functions: `extern const struct qed_eth_ptp_ops qed_ptp_ops_pass;` is the only declaration.

Control flow: No runtime logic; consumers bind to the ops table when PTP support is available in the Ethernet-facing QED API.

State and persistence: No state is stored in the header.

Dependencies/integration: Requires `struct qed_eth_ptp_ops` to be visible through prior QED Ethernet headers at inclusion sites.

Risks: The header has no config stubs, so build configuration must ensure only valid consumers reference the symbol.

Test signals: Compile/link coverage for Ethernet driver paths that include PTP ops and for builds where PTP object code is present.
