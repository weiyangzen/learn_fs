# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_of.c

## Purpose

`nv_of.c` retrieves EDID data for NVIDIA adapters from Open Firmware device-tree properties. It complements I2C DDC probing, especially on PowerPC/Open Firmware systems where firmware already exposes panel or display EDID. The source was read as a complete 78-line file.

## Important APIs, Types, and Functions

The single exported function is `nvidia_probe_of_connector(struct fb_info *info, int conn, u8 **out_edid)`. It searches property names `DFP,EDID`, `LCD,EDID`, `EDID`, `EDID1`, `EDID,B`, and `EDID,A`.

## Control Flow

The function maps the PCI device to its OF node. On dual-head hardware, it scans child nodes and matches connector 1 or 2 by child `"name"` suffix `A` or `B`, then searches the EDID property list. If no child EDID is found, it searches the parent. A found property is duplicated with `kmemdup(EDID_LENGTH, GFP_KERNEL)`, returned through `out_edid`, and logged; otherwise the function returns `-1`.

## State and Persistence Behavior

No persistent state is owned. It allocates an EDID copy for the caller, which is responsible for freeing it. Device-node references are temporarily acquired during child iteration and released with `of_node_put()` when a matching child is found.

## Dependencies and Integration Points

The file depends on PCI-to-OF mapping, device-tree property access, fbdev types, and `../edid.h`. It is called by `NVCommonSetup()` after or alongside I2C EDID probing.

## Risks and Edge Cases

Child-node matching assumes display node names end in `A` or `B`; firmware using other naming conventions may be missed. The code does not validate the EDID property length before copying `EDID_LENGTH`. It returns `-1` for both absence and allocation failure, so callers cannot distinguish missing firmware data from memory pressure.

## Test Signals

Test with OF nodes containing parent-only EDID, dual-head child EDID with `A`/`B` names, missing EDID, and malformed/short EDID properties. Probe should choose the correct head and free returned buffers in `NVCommonSetup()`.
