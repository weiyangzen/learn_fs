# sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv.h

Purpose: Shared internal interface for the FireDTV FireWire DVB driver. It defines common model/status/device state structures and cross-file function prototypes used by AVC, CI, DVB, frontend, FireWire backend, and remote-control modules.

Important APIs/types/functions: `struct firedtv_tuner_status` is the parsed AV/C tuner-status descriptor with RF, BER, signal, C/N, voltage, and CA bits. `enum model_type` identifies unknown, DVB-S, DVB-C, DVB-T, and DVB-S2 devices. `struct firedtv` aggregates device pointer/list membership, DVB adapter/demux/frontend/net/CA objects, AV/C synchronization and buffer state, remote-control work/input state, model/subunit/isochannel, LNB tone/voltage, demux PID filter state, and a 512-byte AV/C data buffer. Prototypes expose the cross-module FireDTV APIs.

Control flow: FireWire probe allocates `struct firedtv`, initializes locks/work, detects model/subunit, then calls functions declared here to register DVB, RC, CA, AV/C, and ISO components. During runtime DVB frontend/demux/CA callbacks all converge on the shared state and AVC helpers.

State and persistence: This header defines the central per-device runtime state. It is all volatile kernel memory; hardware state lives in FireWire/CMP/AVC transactions and is reconstructed on probe/init/tune.

Dependencies/integration: Includes Linux DVB uAPI, media DVB core, demux, dvbnet, mutex/spinlock/wait/workqueue types, and FireWire matching types. It provides input stubs when `CONFIG_DVB_FIREDTV_INPUT` is disabled.

Risks and test signals: Cross-file changes to `struct firedtv` affect lifetime, locking, and callback assumptions across the whole module. Tests should stress concurrent AV/C commands, demux feed changes, remote notifications, CA ioctls, ISO start/stop, remove/update, and disabled RC builds.
