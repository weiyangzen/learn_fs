## sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_snic.h

### Purpose
Defines the SNIC-specific configuration region delivered through Cisco vNIC device configuration. It captures firmware-provided limits and operational defaults for queue depth, data field size, I/O throttling, link-down behavior, LUN fanout, interrupt timer configuration, transport type, and host ID.

### Important APIs, Types, and Constants
- Min/max macros constrain `wq_enet_desc_count`, `maxdatafieldsize`, `io_throttle_count`, `port_down_timeout`, `port_down_io_retries`, and `luns_per_tgt`.
- `struct vnic_snic_config` stores `flags`, `wq_enet_desc_count`, `io_throttle_count`, `port_down_timeout`, `port_down_io_retries`, `luns_per_tgt`, `maxdatafieldsize`, `intr_timer`, `intr_timer_type`, `xpt_type`, and `hid`.

### Control Flow and State
The header is passive. SNIC probe/configuration code reads this structure from device-specific configuration space and copies it into the adapter state. Its fields become persistent runtime configuration for queue sizing, host discovery, SCSI target limits, interrupt coalescing, and firmware throttling.

### Dependencies and Integration Points
The values feed SNIC main/probe setup, SCSI host limit calculation, interrupt initialization, and work queue allocation. `wq_enet_desc_count` aligns with `vnic_wq` descriptor-ring allocation and `io_throttle_count` aligns with SNIC request accounting.

### Risks and Test Signals
The main risk is trusting firmware-provided values without range validation. Probe tests should cover minimum and maximum values, invalid firmware values, and interactions between `luns_per_tgt`, `io_throttle_count`, and SCSI host queue limits.
