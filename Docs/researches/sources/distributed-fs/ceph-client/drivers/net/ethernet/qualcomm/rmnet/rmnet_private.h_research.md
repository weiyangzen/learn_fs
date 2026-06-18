# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_private.h

Purpose: Holds small private RMNET constants shared by RMNET implementation files.

Important definitions: `RMNET_MAX_PACKET_SIZE`, `RMNET_DFLT_PACKET_SIZE`, `RMNET_NEEDED_HEADROOM`, and `RMNET_TX_QUEUE_LEN` define virtual device sizing defaults. `RMNET_EPMODE_VND` and `RMNET_EPMODE_BRIDGE` select whether ingress frames are delivered to a virtual RMNET device or forwarded directly to a bridge endpoint.

Control flow and integration: The mode constants are consumed by `rmnet_handlers.c`. MTU, headroom, and queue length constants are consumed by `rmnet_vnd.c` during device setup and MTU validation.

State and persistence: No runtime state is stored here. The constants shape persistent net_device configuration once VND devices are created.

Risks and test signals: Changes affect device MTU bounds, headroom guarantees for MAP/checksum headers, and handler mode dispatch. Build tests plus create/change-MTU/link tests should verify constants remain compatible with MAP header growth and real-device MTU.
