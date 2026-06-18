# sources/distributed-fs/ceph-client/include/linux/soc/qcom/wcnss_ctrl.h

Purpose: This header exposes a Qualcomm WCNSS control helper for opening named rpmsg channels.

Important APIs/types/functions: It declares `qcom_wcnss_open_channel(void *wcnss, const char *name, rpmsg_rx_cb_t cb, void *priv)` returning an `rpmsg_endpoint`.

Control flow: A WCNSS consumer requests a channel by name, provides an RX callback and private pointer, then uses the returned endpoint for rpmsg communication.

State and persistence: Channel and endpoint state are managed by the WCNSS/rpmsg core. Remote WLAN firmware owns channel availability across subsystem restarts.

Dependencies and integration: Integrates with rpmsg, Qualcomm WCNSS remoteproc/control drivers, WLAN/Bluetooth/FM clients, and subsystem restart handling.

Risks and test signals: Channel-name mismatch or SSR during open can fail endpoint creation. Test channel open/close, RX callback dispatch, remote restart, and missing firmware channel behavior.
