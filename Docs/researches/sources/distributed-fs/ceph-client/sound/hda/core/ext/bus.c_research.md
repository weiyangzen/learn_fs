# sources/distributed-fs/ceph-client/sound/hda/core/ext/bus.c

## Purpose
`ext/bus.c` initializes and tears down an extended HD-audio bus and registers HDA drivers for ASoC-style extended devices (`HDA_DEV_ASOC`).

## Important APIs, Types, and Functions
Exports are `snd_hdac_ext_bus_init()`, `snd_hdac_ext_bus_exit()`, `snd_hdac_ext_bus_device_remove()`, `snd_hda_ext_driver_register()`, and `snd_hda_ext_driver_unregister()`. Internal wrappers adapt `struct device_driver` callbacks to `struct hdac_driver` probe/remove/shutdown methods.

## Control Flow
Extended bus init calls base `snd_hdac_bus_init()`, stores ext ops, assigns bus index 0, and marks command DMA active. Exit calls base exit and warns if hlink objects remain. Device removal iterates codec devices, unregisters them, and drops references. Driver register sets type to `HDA_DEV_ASOC`, uses `snd_hda_bus_type`, installs callback wrappers, and registers with the driver core.

## State and Persistence Behavior
State lives in the base `hdac_bus` plus `ext_ops`, `idx`, `cmd_dma_state`, and `hlink_list`. Driver registration mutates the supplied `hdac_driver` object before registering it.

## Dependencies and Integration Points
It depends on base HDA bus code, Linux driver core, and `sound/hdaudio_ext.h`. Consumers are extended HDA/ASoC codec drivers and controller integrations.

## Risks
The bus index is fixed at 0, with a FIXME for multi-bus systems. Exit only warns about leaked links; consumers must free them. Driver wrappers assume callbacks are valid when installed.

## Test Signals
Test ext bus init/exit, ASOC driver match/probe/remove/shutdown, device removal over multiple codecs, and no hlink leaks before exit.
