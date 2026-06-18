<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/bus.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/bus.c

## Purpose
Provides common nvkm_i2c_bus lifecycle, adapter registration, pad arbitration, Linux I2C algorithm selection, and device probing helpers.

## Important APIs, Types, And Functions
Important APIs include nvkm_i2c_bus_init/fini/acquire/release/probe/del/ctor/new_, nvkm_i2c_bus_xfer, nvkm_i2c_bus_pre_xfer/post_xfer, and line drive/sense callbacks for i2c-algo-bit.

## Control Flow
Constructor registers an i2c_adapter either with Linux i2c_bit_algo using drive/sense callbacks or with a custom algorithm calling bus->func->xfer. Transfers acquire the bus mutex and pad in I2C mode, call backend xfer, then release. Probe temporarily adjusts bit-bang udelay for specific devices and scans candidate addresses.

## State, Persistence, Dependencies, And Integration
State includes bus enabled flag, mutex, pad pointer, id, i2c_adapter, optional algo_data, and backend function table. Dependencies are Linux I2C core, core options NvI2C, and pad arbitration. Integration points are BIOS-created DDC buses, iccsense sensors, external encoder upstream I2C, and display EDID paths.

## Risks And Test Signals
Risks: bus->func constructor return values are not always checked by chip-specific new functions; pad contention yields -EBUSY; adapter registration failures must unwind via nvkm_i2c_bus_del. Test signals include adapter enumeration, EDID/I2C transfers through both algorithm modes, probe detection logs, and suspend/resume enable gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/bus.c -->
