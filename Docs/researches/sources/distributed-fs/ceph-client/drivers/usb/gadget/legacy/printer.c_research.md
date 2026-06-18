# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/printer.c

Purpose: legacy `g_printer` composite wrapper around the printer function, exposing a USB printer-class gadget with configurable serial, PNP string, and endpoint request queue length.

Important APIs, types, and functions: module parameters `iSerialNum`, `iPNPstring`, and `qlen` feed composite overrides and `f_printer_opts`. `printer_bind` gets the `"printer"` function instance, sets minor and queue length, installs the PNP string, assigns string IDs, allocates optional OTG descriptors, and registers `printer_cfg_driver`. `printer_do_config` resets endpoint autoconfig, marks self-powered, applies OTG descriptors, gets `f_printer`, and adds it. `printer_unbind` releases function resources.

Control flow: bind prepares function options before registering the configuration. During config bind, the printer function is added to the single configuration. On error, function instance and OTG descriptor ownership are unwound; allocated PNP string ownership is delegated to printer function cleanup as noted in the code.

State and persistence: global descriptor strings and function pointers persist while the module is loaded. Runtime printer buffering and device node behavior live in `u_printer`/`f_printer`. No durable state is written.

Dependencies and integration points: depends on libcomposite, USB printer UAPI definitions, and `u_printer.h`. It exposes a printer gadget that typically creates a gadget-side printer character device through the function implementation.

Risks: `qlen` affects memory use and throughput. PNP string allocation/ownership relies on lower-level cleanup. Endpoint autoconfig reset is required before adding the function, and missing it can produce endpoint conflicts. Host printer-class behavior is descriptor-string sensitive.

Test signals: enumerate with default and custom PNP strings, inspect printer class descriptors, verify gadget-side printer device I/O, test large queue lengths, disconnect during active transfers, and unload while confirming function and OTG descriptor release.
