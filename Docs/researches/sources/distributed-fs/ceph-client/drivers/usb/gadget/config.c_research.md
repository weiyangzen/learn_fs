# sources/distributed-fs/ceph-client/drivers/usb/gadget/config.c

## Purpose
`config.c` provides small but central descriptor utilities used by USB gadget function and composite drivers. It copies null-terminated descriptor vectors, marshals descriptor arrays into EP0/configuration buffers, assigns per-speed descriptor copies to a `usb_function`, frees them, and builds OTG descriptors based on gadget OTG capabilities.

## Important APIs, Types, and Functions
Exports are `usb_descriptor_fillbuf()`, `usb_copy_descriptors()`, `usb_assign_descriptors()`, `usb_free_all_descriptors()`, `usb_otg_descriptor_alloc()`, and `usb_otg_descriptor_init()`. The code operates on `struct usb_descriptor_header **` vectors, `struct usb_function` descriptor slots (`fs_descriptors`, `hs_descriptors`, `ss_descriptors`, `ssp_descriptors`), and OTG descriptor types `struct usb_otg_descriptor` and `struct usb_otg20_descriptor`.

## Control Flow
`usb_descriptor_fillbuf()` walks a descriptor pointer array until NULL, copying each descriptor length into the destination if it fits. `usb_copy_descriptors()` first counts descriptors and total bytes, allocates one contiguous block for pointer vector plus descriptor bytes, then rewrites vector entries to point inside that block. `usb_assign_descriptors()` copies supplied FS/HS/SS/SSP vectors into the function; absent SSP falls back to SS. On any allocation failure it calls `usb_free_all_descriptors()` to leave no partial descriptor state. OTG allocation chooses descriptor size by `gadget->otg_caps->otg_rev`; initialization fills SRP/HNP/ADP capability bits and bcdOTG where applicable.

## State and Persistence
All descriptor state is heap allocated and owned by the function after assignment. The vectors are per-function copies so bind routines can patch static templates before assignment without later mutations affecting already-bound functions. OTG descriptors are separately allocated and typically hung off configuration descriptor arrays by callers. Nothing persists across unbind; callers must free through `usb_free_all_descriptors()` and `kfree()` for OTG allocations.

## Dependencies and Integration Points
The composite framework uses `usb_descriptor_fillbuf()` when building configuration descriptors and function drivers use `usb_assign_descriptors()` after endpoint/interface/string IDs are assigned. The file depends on USB chapter 9 descriptor definitions, gadget OTG capability structures, and `usb_free_descriptors()` from the gadget API.

## Risks
Descriptor vectors must be NULL-terminated and each descriptor's `bLength` must be correct; malformed templates can cause incorrect allocation size or EP0 copy failure. `usb_descriptor_fillbuf()` returns `-EINVAL` if a descriptor does not fit, so callers must propagate that to avoid truncated descriptors. SSP fallback to SS is intentional but can mask lack of true SuperSpeedPlus descriptors. OTG initialization assumes `otg_caps` is coherent when `otg_rev >= 0x0200`.

## Test Signals
Check descriptor copy/free under allocation fault injection, configuration descriptor building with too-small buffers, FS/HS/SS/SSP enumeration with functions that omit SSP descriptors, and OTG 1.x versus 2.0 descriptor generation for gadgets with different `otg_caps` combinations.
