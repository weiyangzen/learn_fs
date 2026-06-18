# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/base.c

## Purpose
Implements common voltage table parsing, voltage/VID mapping, conditional voltage setting, speedo handling, and subdev construction.

## Important APIs, Types, And Functions
Important APIs include `nvkm_volt_get()`, `nvkm_volt_map_min()`, `nvkm_volt_map()`, `nvkm_volt_set_id()`, `nvkm_volt_ctor()`, and `nvkm_volt_new_()`.

## Control Flow
Constructor parses VBIOS voltage and VMAP tables into VID entries, min/max microvolts, and max voltage IDs. Oneinit reads speedo and calls chip oneinit. Set-by-ID maps VBIOS voltage IDs through polynomial/linked VMAP entries, applies min IDs and condition direction, then sets either direct voltage or VID.

## State, Persistence, And Dependencies
State includes VID table entries, min/max voltage, VID mask, speedo, max voltage IDs, and chip callbacks in `struct nvkm_volt`.

## Integration Points
Depends on BIOS volt/vmap parsers, thermal temperature inputs for maps, GPIO or PWM/regulator chip callbacks, and fuse speedo readers.

## Risks
Mapping math is version/mode sensitive and uses fixed-point integer formulas. Missing speedo blocks mapped voltage. Conditional updates rely on accurate current voltage reads.

## Test Signals
Signals include parsed VID debug lines, current voltage logs, correct voltage changes for pstate transitions, and graceful handling of missing BIOS data.
