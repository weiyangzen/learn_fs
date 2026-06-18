# sources/distributed-fs/ceph-client/drivers/usb/gadget/u_os_desc.h

Purpose: inline helper header for building Microsoft OS extended property descriptors in little-endian layout.

Important APIs, types, and functions: constants define offsets and property data types. Pointer helpers return locations for size, type, name length, name, data length, and data. Writer helpers include `usb_ext_prop_put_size`, `usb_ext_prop_put_type`, `usb_ext_prop_put_name`, `usb_ext_prop_put_binary`, and `usb_ext_prop_put_unicode`.

Control flow: callers pass a preallocated descriptor buffer. The helpers write unaligned little-endian fields, convert UTF-8 strings to UTF-16LE for property names/data, add UTF-16 NUL terminators, and return either written lengths or conversion errors.

State and persistence: no state. The buffer and bounds are entirely caller-owned.

Dependencies and integration points: depends on `linux/unaligned.h` and `linux/nls.h`. Used by gadget configfs/function code that advertises OS descriptors to Windows hosts.

Risks: helpers do not validate total buffer capacity, so caller-side size computation must be correct. `usb_ext_prop_put_unicode` uses `data_len >> 1` as the source character count for UTF-8 conversion, which assumes caller passes compatible sizing. Offsets depend on the OS descriptor format and must not drift.

Test signals: build descriptors with ASCII and multibyte UTF-8 property names/data, verify little-endian fields and terminators, test binary property placement, run with undersized buffers under KASAN in callers, and validate enumeration on Windows OS descriptor consumers.
