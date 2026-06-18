<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/base.c

## Purpose
Constructs and manages Nouveau I2C pads, bit-bang/native I2C buses, AUX channels, external encoder pads, and AUX interrupt events from BIOS DCB tables.

## Important APIs, Types, And Functions
Important APIs include nvkm_i2c_bus_find, nvkm_i2c_aux_find, nvkm_i2c_intr, nvkm_i2c_preinit/init/fini/dtor, nvkm_i2c_new_, and the internal nvkm_i2c_drv table mapping ANX9805 extdev IDs to anx9805_pad_new.

## Control Flow
Constructor parses DCB I2C entries, creates shared or per-CCB pads, creates bus objects based on DCB type and pad capabilities, creates AUX objects for NVIO_AUX/PMGR entries, then parses display outputs for external encoders and creates external ANX9805 bus/AUX children. Preinit brings up pads/buses early for VBIOS scripts; init also enables AUX; fini disables AUX/buses/pads and masks/acks interrupts; intr reads aux_stat and emits NVKM_I2C_PLUG/UNPLUG/IRQ/DONE events per aux id.

## State, Persistence, Dependencies, And Integration
State includes i2c pad/bus/aux lists, event object, enabled state inside children, and BIOS-derived IDs. Dependencies are BIOS DCB/I2C/output parsers, nvkm_event, generation-specific pad funcs, and ANX9805 support. Integration points are display probing, EDID/DDC, DP AUX/hotplug, VBIOS init scripts, and power-sensor I2C users.

## Risks And Test Signals
Risks: malformed BIOS entries can create no bus/aux or ignored CCBs; primary/secondary bus remapping depends on DCB I2C table version; external encoders require known extdev IDs. Test signals include CCB debug logs, I2C adapter registration, EDID read on primary/secondary buses, AUX hotplug event delivery, and clean teardown with no list leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/base.c -->
