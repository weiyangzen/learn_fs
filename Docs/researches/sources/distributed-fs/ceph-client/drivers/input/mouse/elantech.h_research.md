# sources/distributed-fs/ceph-client/drivers/input/mouse/elantech.h

`elantech.h` defines the Elantech protocol contract: query/register command constants, retry timing, hardware coordinate ranges, packet identifiers, bus-provider constants, `ETP_NEW_IC_SMBUS_HOST_NOTIFY()`, and the shared structures used by `elantech.c`.

The key types are `struct elantech_device_info`, which stores firmware/hardware version, capabilities, geometry, resolution, bus and quirk flags, and command helper; and `struct elantech_data`, which stores live cached registers, parity, multitouch positions, optional TrackPoint state, and the original rate setter. Exported entry points are `elantech_detect()`, `elantech_init_ps2()`, `elantech_init()`, and `elantech_init_smbus()`.

The header drives control flow through version constants and Kconfig stubs. State is runtime-only and per-device. Integration points are psmouse core and optional SMBus/Elan I2C routing. Risks are incorrect constants affecting geometry, packet dispatch, or bus choice. Test signals include Kconfig build coverage, correct input ranges, firmware-to-version mapping, and expected SMBus decisions.
