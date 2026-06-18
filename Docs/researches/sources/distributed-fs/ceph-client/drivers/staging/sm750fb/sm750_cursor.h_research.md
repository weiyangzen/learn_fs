## sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_cursor.h

Purpose: this small header declares the SM750 hardware cursor operations consumed by the framebuffer driver.

Important APIs: prototypes cover cursor enable/disable, size, position, color, and two cursor data packing variants: `sm750_hw_cursor_set_data()` and `sm750_hw_cursor_set_data2()`.

Control flow and state: this file has no state or executable logic. The API operates on `struct lynx_cursor`, whose definition is provided by `sm750.h`; include ordering therefore matters because the header does not forward-declare the structure.

Dependencies and integration points: included by `sm750.c` and `sm750_cursor.c`. It is private to the staging driver and is wired into fbdev through `lynxfb_ops_cursor()`.

Risks: the header exposes two data-packing functions without documenting their difference or expected bit order. It also relies on external definitions of `u8`, `u16`, `u32`, and `struct lynx_cursor`, so standalone inclusion is fragile.

Test signals: compile coverage for include ordering and runtime cursor behavior through the fbdev cursor callback are sufficient for this header.
