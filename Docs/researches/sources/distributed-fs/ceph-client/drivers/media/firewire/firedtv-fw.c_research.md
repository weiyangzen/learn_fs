# sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-fw.c

Purpose: Provides the FireDTV FireWire bus backend. It handles FireWire transactions, isochronous MPEG-TS reception, FCP response routing, device probe/remove/update, model detection, DVB/RC registration, and module init/exit address-handler registration.

Important APIs/types/functions: `node_req()` wraps `fw_run_transaction()` for lock/read/write operations exported as `fdtv_lock()`, `fdtv_read()`, and `fdtv_write()`. ISO receive state is `struct fdtv_ir_context`; `queue_iso()`, `handle_iso()`, `fdtv_start_iso()`, and `fdtv_stop_iso()` manage receive buffers and feed TS packets to `dvb_dmx_swfilter_packets()`. `handle_fcp()` routes FCP responses to the matching `struct firedtv` in `node_list`. Probe/remove/update callbacks are `node_probe()`, `node_remove()`, and `node_update()`. Module init registers an FCP response address handler and the FireWire driver.

Control flow: Probe allocates and initializes `struct firedtv`, reads the CSR model string, maps it to a model enum, registers remote control if enabled, adds the node to the global list for FCP routing, identifies the AV/C subunit, registers DVB devices, and registers remote-control notifications. Remove unregisters DVB, removes the node from FCP routing, unregisters RC, and frees state. ISO start creates a FireWire receive context, initializes DMA pages, queues 64 packets, starts matching all tags, and stores the context; the callback strips ISO/CIP/source headers and sends 188-byte MPEG-TS packets to the demux.

State and persistence: Global runtime state is `node_list` protected by `node_list_lock` and one FCP address handler. Per-device state is `struct firedtv`, including workqueue item, mutexes, DVB objects, ISO context pointer, model type, subunit, and channel. No persistent storage exists.

Dependencies/integration: Depends on Linux FireWire core, FireWire CSR constants, DMA page-backed ISO buffers, DVB demux, and all FireDTV internal modules. The device ID table matches Digital Everywhere OUIs/models/specifier/version.

Risks and test signals: Test probe failure unwind at every stage, model string length/matching, FCP routing across bus generation changes, node update while streaming, ISO packet length/header parsing, queue/requeue failures, stop with missing context, remove while work/ISO/FCP callbacks are active, and multiple devices. `fdtv_stop_iso()` assumes `fdtv->ir_context` is valid, and model type defaults to zero if no string matches, so invalid hardware paths require coverage.
