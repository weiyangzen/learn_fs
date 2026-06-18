<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/conn.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/conn.c

Purpose: creates and destroys display connector objects from VBIOS connector table entries and translates BIOS HPD bitmasks into GPIO line numbers.

Important APIs and functions: `nvkm_conn_new()` allocates and constructs a `struct nvkm_conn`; `nvkm_conn_del()` removes and frees it. `nvkm_conn_ctor()` copies `struct nvbios_connE`, initializes the HPD field to unused, logs connector metadata, maps BIOS HPD bit positions through a static `hpd[]` function table, and resolves the actual GPIO line with `nvkm_gpio_find()`.

Control flow: construction is linear. If the BIOS HPD mask is empty, the connector remains without HPD. If the bit index is out of the supported table or GPIO lookup fails, construction keeps the object but leaves `conn->info.hpd` unused and logs an error.

State and persistence: persistent connector state includes display pointer, connector index, copied BIOS connector info, list node, and object base. HPD line translation is stored in `conn->info.hpd`.

Dependencies and integration points: depends on BIOS connector parsing, GPIO subdevice lookup, display object lists, and output creation/HPD event paths that consume `conn->info`.

Risks: BIOS HPD bit encoding is hardware/firmware-specific; an unmapped index disables hotplug detection for that connector. Keeping construction successful after HPD errors is deliberate but can hide broken hotplug until runtime.

Test signals: parse connector tables on systems with internal panels, DP/HDMI, and no-HPD outputs; verify HPD GPIO line resolution and hotplug events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/conn.c -->
