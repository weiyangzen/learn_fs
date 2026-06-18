<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dvb-bt8xx.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dvb-bt8xx.c

Purpose: Implements the Bt8xx DVB adapter glue between the bttv subdevice layer, the BT878 DMA core, Linux DVB demux/net devices, and board-specific frontend/tuner chips. It turns completed BT878 DMA transport-stream blocks into DVB software demux input and registers one DVB adapter per supported bttv board.

Important APIs/functions: `dvb_bt8xx_probe()` allocates `struct dvb_bt8xx_card`, maps bttv board type to GPIO/DMA mode fields, matches the companion `bt878` DMA device, and calls `dvb_bt8xx_load_card()`. `dvb_bt8xx_load_card()` registers the DVB adapter, demux, dmxdev, hardware/memory frontends, DVB net device, work item, and frontend. `frontend_init()` is the central board switch for MT352/ZL10353, LGDT330x, NXT6000, SP887x, DST, CX24110, and OR51211 frontends plus simple tuner attachments and tuner callbacks. `dvb_bt8xx_start_feed()`/`stop_feed()` reference count active demux feeds and start/stop BT878 DMA. `dvb_bt8xx_work()` consumes `finished_block` ring-buffer slots via `dvb_dmx_swfilter()` or `_204()`.

Control flow: module init registers a bttv sub-driver named `dvb`; probe selects board parameters, finds matching BT878 core by PCI slot/subsystem IDs, then builds the DVB stack. Streaming begins on the first demux feed, the BT878 core fills a cyclic buffer, and the bottom-half work drains all blocks between `last_block` and `finished_block` into DVB demux filtering. Remove stops DMA, cancels work, unregisters DVB net/demux/frontend/adapter objects, and frees card state.

State/persistence: Runtime state is in `struct dvb_bt8xx_card` plus BT878 fields such as `last_block`, `finished_block`, `block_bytes`, and `TS_Size`. `nfeeds` is protected by `card->lock`; the BT878 GPIO lock is initialized in probe. No on-disk persistence exists. Module parameters are `debug` and DVB adapter numbering.

Dependencies/integration: Depends on bttv subdevices, `bt878`, DVB core/demux/net APIs, I2C, frontend drivers, tuner-simple, firmware requests for SP887x and OR51211, and board IDs from bttv. It directly toggles bttv GPIO lines for resets, relays, and frontend mode selection.

Risks: Board support is a large hard-coded switch with chip-specific magic values and GPIO timing. Feed reference counting assumes balanced DVB demux callbacks; underflow would stop DMA incorrectly. Firmware request paths depend on the BT878 PCI device. Matching BT878 to bttv uses PCI slot/subsystem equality and may fail if another driver such as ALSA bt87x already owns the DMA core. Workqueue draining depends on coherent BT878 ring indices.

Test signals: Probe/remove on each supported board, frontend attach success/failure logs, DVB adapter registration, transport-stream capture, first-feed start and last-feed stop, firmware loading for affected boards, GPIO reset behavior, and error unwinds in `dvb_bt8xx_load_card()` are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dvb-bt8xx.c -->
