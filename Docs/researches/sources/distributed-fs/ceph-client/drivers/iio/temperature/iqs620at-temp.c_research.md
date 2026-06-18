# sources/distributed-fs/ceph-client/drivers/iio/temperature/iqs620at-temp.c

Purpose: platform IIO temperature child driver for the Azoteq IQS620AT MFD. It exposes one direct-mode temperature channel with raw, scale, and hardware-version-dependent offset.

Important APIs/types/functions: `iqs620_temp_read_raw()` reads `IQS620_TEMP_UI_OUT` via the parent regmap, returns scale 1000, and chooses offset `-100` or `-40` depending on `hw_num`. Probe gets `struct iqs62x_core` from the parent and stores it as IIO driver data.

Control flow: probe allocates an IIO device with no private allocation, attaches parent core data, fills channel/info/name fields, and registers. Raw read performs a little-endian 16-bit register read on demand.

State and persistence: no local mutable state; all hardware access goes through the MFD core regmap. Offset depends on immutable hardware number.

Dependencies/integration: depends on MFD_IQS62X platform data, regmap, and IIO direct mode. Module alias is `platform:iqs620at-temp`.

Risks and test signals: parent lifetime and regmap serialization are delegated to the MFD core. Test V2/V3 offset selection, endian conversion, parent-driver probe ordering, raw read errors, and IIO scale/offset ABI.
