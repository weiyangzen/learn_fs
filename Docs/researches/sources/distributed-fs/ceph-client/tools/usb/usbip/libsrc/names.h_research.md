# sources/distributed-fs/ceph-client/tools/usb/usbip/libsrc/names.h

Purpose: `names.h` declares the USB name database interface implemented by `names.c`.

Important APIs: it exports lookup functions for vendor, product, class, subclass, and protocol names, plus `names_init(char *n)` to load a database and `names_free()` to release memory. The API uses fixed-width USB ID types from `<sys/types.h>`.

Control flow and integration: callers normally use the wrappers in `usbip_common.c` (`usbip_names_init()`, `usbip_names_get_product()`, and `usbip_names_get_class()`) rather than formatting directly. `usbip_list` and `usbip_port` initialize names around user-visible listing commands.

State, dependencies, risks, and tests: the header itself has no state, but the implementation behind it is global and process-wide. It has no const-correctness on the input path. Risks are limited API documentation and no explicit reinitialization contract. Test signals are compile-time consistency with `names.c` and correct name lookups after `names_init()`.
