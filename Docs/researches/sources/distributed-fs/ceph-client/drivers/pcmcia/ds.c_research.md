# sources/distributed-fs/ceph-client/drivers/pcmcia/ds.c

Purpose: Implements the 16-bit PCMCIA bus and driver services layer. It registers PCMCIA drivers, creates `pcmcia_device` instances from socket CIS data, performs device/driver matching, handles dynamic IDs and firmware CIS overrides, exposes device sysfs attributes, coordinates per-device PM, and registers as a class interface for sockets.

Important APIs and functions: Exported APIs are `pcmcia_register_driver()`, `pcmcia_unregister_driver()`, and `pcmcia_dev_present()`. Major internals include `pcmcia_device_probe()`, `pcmcia_device_remove()`, `pcmcia_device_query()`, `pcmcia_device_add()`, `pcmcia_card_add()`, `pcmcia_requery()`, `pcmcia_load_firmware()`, `pcmcia_devmatch()`, `pcmcia_bus_match()`, PM helpers, and socket callbacks in `pcmcia_bus_callback`.

Control flow: Driver registration fills a `device_driver`, checks product-string hashes, registers on `pcmcia_bus_type`, and creates a `new_id` sysfs file. Socket class-interface add creates the socket CIS bin file, initializes device lists/counts, and registers callbacks with `cs.c`. On card add, the layer waits for resource setup, validates memory and CIS, detects multifunction chains, allocates devices per function, queries MANFID/FUNCID/VERS data, sets up IRQ/config resources, and registers devices. Driver matching tries dynamic IDs first, then static ID tables, with guarded FUNCID fallback and optional fake CIS firmware loading.

State and persistence: Runtime state includes driver dynamic ID lists, socket device lists, `device_count`, `pcmcia_pfc`, `present`, per-device identity fields, product strings, config resources, suspend flags, and function shared `config_t`. CIS firmware overrides persist only in the socket's fake CIS memory until card/socket removal.

Dependencies and integration points: Uses Linux device model bus/class interfaces, firmware loader, CRC32 modalias hashing, DMA mask setup, CIS tuple helpers, resource APIs, socket callbacks, sysfs attributes, and runtime/system PM.

Risks: Matching behavior is intentionally conservative: FUNCID matching requires userspace acknowledgement to avoid binding wrong drivers. Pseudo multifunction cards share configuration state and can trigger requery/removal cascades. Firmware CIS loading can change function count and force re-enumeration. Device removal checks for unreleased IRQ/I/O/window resources but cannot fully protect against buggy drivers.

Test signals: Register legacy PCMCIA drivers, dynamic `new_id`, modalias generation, udev autoload, fake CIS firmware, pseudo multifunction cards, sysfs attributes, suspend/resume via `pm_state`, card requery after CIS changes, and driver cleanup warnings.
