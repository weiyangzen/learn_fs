<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dvb-bt8xx.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dvb-bt8xx.h

Purpose: Defines the private card object for the bt8xx DVB adapter and gathers the external frontend, tuner, bttv, DVB, I2C, and mutex declarations needed by `dvb-bt8xx.c`.

Important APIs/types: `struct dvb_bt8xx_card` is the driver-owned state container. It holds synchronization (`lock`), feed count (`nfeeds`), card naming, `dvb_adapter`, BT878 pointer, bttv index, demux/dmxdev/frontend objects, BT878 GPIO/DMA mode masks, I2C adapter, DVB net state, and the attached `struct dvb_frontend *fe`.

Control flow: This header has no executable flow. Its fields are filled during probe, consumed during streaming/feed callbacks, and unwound during remove.

State/persistence: All fields are volatile per-device kernel state. The most important lifecycle-sensitive members are `bt`, `i2c_adapter`, `demux`, `dmxdev`, `dvbnet`, and `fe`, because cleanup order in the C file depends on them being initialized consistently.

Dependencies/integration: Includes bttv and a broad set of frontend headers (`mt352`, `sp887x`, `dst_common`, `nxt6000`, `cx24110`, `or51211`, `lgdt330x`, `zl10353`, `tuner-simple`). This tight coupling mirrors the board switch in the implementation.

Risks: The struct is shared across asynchronous work, DVB callbacks, and remove. Any future field additions that affect streaming need clear locking or teardown ordering. The header exposes no helper API, so the implementation must maintain lifecycle discipline manually.

Test signals: Compile coverage with all selected frontend dependencies, probe/remove smoke tests, and DVB streaming tests that exercise fields across feed start/stop and workqueue processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dvb-bt8xx.h -->
