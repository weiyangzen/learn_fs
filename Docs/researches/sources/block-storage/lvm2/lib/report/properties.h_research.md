# File Research: sources/block-storage/lvm2/lib/report/properties.h

## Purpose

`properties.h` declares the liblvm property access API implemented by `properties.c`.

## API Surface

It includes device-mapper, metadata, reporting, and common property definitions, then declares:

- LV segment property get: `lvseg_get_property`
- LV property get/set: `lv_get_property`, `lv_set_property`
- VG property get/set: `vg_get_property`, `vg_set_property`
- PV segment property get: `pvseg_get_property`
- PV property get/set: `pv_get_property`, `pv_set_property`

## Design Notes

- All APIs take a concrete LVM metadata object plus a mutable `struct lvm_property_type *prop`.
- Getters fill the requested property from the internal `_properties[]` table.
- Setters are available only where the property table marks a field as writeable and a setter implementation exists.
- The header is narrow and intentionally does not expose `_properties[]` or the generated getter/setter internals.
