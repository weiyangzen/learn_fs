## sources/distributed-fs/ceph-client/include/uapi/linux/dvb/ca.h

Purpose: This DVB conditional-access UAPI exposes Common Interface slots, descrambler capabilities, CAM messaging, and descrambler control-word programming.

Important APIs and types: `struct ca_slot_info` describes slot number, type (`CA_CI`, `CA_CI_LINK`, `CA_CI_PHYS`, `CA_DESCR`, `CA_SC`) and flags for module present/ready. `struct ca_descr_info` reports descrambler count and type (`CA_ECD`, `CA_NDS`, `CA_DSS`). `struct ca_caps` reports aggregate slot and descrambler capabilities. `struct ca_msg` carries up to 256 bytes to or from a CI CAM. `struct ca_descr` carries an 8-byte control word for a descrambler slot and parity. Ioctls reset, get capabilities, get slot/descrambler info, get/send CAM messages, and set descrambler words.

Control flow and state: Applications query CA capabilities and slot readiness, exchange messages with CAM modules, and program control words for descrambling. Slot insertion/readiness and descrambler key state persist in the driver/hardware until changed, reset, or removed.

Persistence and dependencies: Runtime state lives in CAM hardware, smart cards, and descrambler slots. No durable state is defined. Legacy userspace typedefs are provided outside `__KERNEL__`.

Integration points: CA is used with DVB demux and decoder pipelines to descramble protected MPEG-TS streams. CAM message protocols sit above this raw transport structure.

Risks and test signals: Risks include control-word sensitivity, insufficient bounds checking on `length`, parity slot confusion, slot hotplug races, and legal/security constraints around descrambling. Tests should cover slot presence/ready transitions, cap reporting, max-length message send/receive, invalid descrambler indices, reset effects, and key clearing behavior during module removal.
