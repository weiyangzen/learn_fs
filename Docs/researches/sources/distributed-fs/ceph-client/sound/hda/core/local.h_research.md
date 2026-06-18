## sources/distributed-fs/ceph-client/sound/hda/core/local.h

Purpose: private HD-audio core header that shares internal helpers between core source files without exposing them as public sound API.

Important APIs, types, and functions: declares `hdac_dev_attr_groups`, widget sysfs lifecycle helpers, bus device add/remove/event/verb helpers, and `snd_hdac_exec_verb()`. It references `struct hdac_bus`, `struct hdac_device`, `hda_nid_t`, and `u32` via included users.

Control flow: no executable logic. The declarations connect sysfs, device, bus, and verb execution implementation files so they can call each other while keeping external headers narrower.

State and persistence: no state is defined in the header; it exposes functions that operate on caller-owned bus and codec state.

Dependencies and integration points: included by `regmap.c`, `sysfs.c`, and other HDA core implementation units. It acts as an internal boundary around sysfs attributes, widget tree maintenance, and verb dispatch.

Risks: because it is private, declarations must stay synchronized with implementations; accidental use outside core would couple external drivers to unstable internals. Missing includes in users can make type visibility fragile.

Test signals: compile HD-audio core after signature changes; check that only intended core files include it; verify exported public APIs remain in `<sound/hdaudio.h>` or related public headers.
