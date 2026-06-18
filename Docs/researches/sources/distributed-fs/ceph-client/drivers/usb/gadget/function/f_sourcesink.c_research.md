# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_sourcesink.c

## Purpose
`f_sourcesink.c` implements the source/sink USB gadget test function used by the zero gadget family. It continuously sources data to the host on IN endpoints and sinks data from the host on OUT endpoints, with optional data-pattern validation and optional isochronous endpoints. Its primary purpose is USB controller, endpoint, throughput, and compliance testing.

## Important APIs, types, and functions
`struct f_sourcesink` embeds `struct usb_function` and stores bulk and isochronous endpoints, current alternate setting, pattern mode, isochronous interval/maxpacket/mult/maxburst, bulk buffer length, bulk maxburst, and queue depths. Descriptor tables expose altsetting 0 with two bulk endpoints and altsetting 1 with two bulk plus two isochronous endpoints when the UDC can autoconfigure isoch endpoints. Full-, high-, and super-speed descriptors are patched from configfs options.

`sourcesink_bind()` allocates the interface ID, clamps burst/interval values, autoconfigures bulk and optional iso endpoints, patches endpoint addresses and companion descriptors, disables altsetting 1 descriptors if iso endpoints are unavailable, and assigns descriptors. `check_read_data()` validates OUT buffers against all-zero or mod63 patterns, while pattern 2 disables validation. `reinit_write_data()` fills IN buffers. `source_sink_complete()` validates OUT completions, refills IN data when needed, and resubmits requests until shutdown or fatal queue error. `source_sink_start_ep()` allocates and queues `bulk_qlen` or `iso_qlen` requests. `enable_source_sink()` and `disable_source_sink()` manage endpoint enablement for selected altsetting. `sourcesink_setup()` implements vendor-specific control write/read tests `0x5b` and `0x5c`.

## Control flow
Configfs instance allocation initializes defaults from `g_zero.h`. Function allocation copies options into the function object, freezing settings while `refcnt` is nonzero. Bind prepares descriptors and endpoints. Each `set_alt` first disables active endpoints, then enables bulk endpoints, queues IN and OUT bulk requests, and, for altsetting 1, enables and queues iso endpoints if present. Completion callbacks recycle requests by immediately requeueing them, creating continuous traffic. Disable tears down endpoints; `free_func` decrements the options refcount and frees descriptors.

## State and persistence
State consists of copied configfs options, selected altsetting, endpoint enablement, and in-flight USB requests. No user data is retained except the shared ep0 buffer used by the control write/read test. Options live in `struct f_ss_opts` and are mutable only while no function references the instance. There is no persistent storage.

## Dependencies and integration points
The file depends on USB composite, `linux/usb/func_utils.h` allocation helpers, and `g_zero.h` defaults plus `lb_modinit()`/`lb_modexit()` for the loopback companion function. It registers `SourceSink` manually in module init and initializes loopback support in the same module. It integrates with host-side USB test tools, including control transfer tests modeled after USB compliance devices.

## Risks and edge cases
The function intentionally stresses controllers. Bad pattern data halts the OUT endpoint. Queue allocation failures during startup can leave a partially enabled endpoint stack that must unwind correctly. Optional iso endpoint absence mutates descriptor arrays by nulling altsetting 1 offsets, affecting the advertised interface. Configfs accepts zero queue lengths and buffer lengths where the resulting behavior should be understood by tests. Control request `0x5b` leaves data in the shared ep0 buffer for `0x5c`, so intervening control transfers could overwrite it. Continuous requeueing can amplify UDC DMA, SG, or shutdown races.

## Test signals
Tests should validate descriptor sets for altsetting 0 and optional altsetting 1, configfs rejection of invalid pattern/mult/burst/packet values while allowing changes before use, bulk and iso traffic at full/high/super speed, pattern modes 0, 1, and 2, endpoint halt on corrupted OUT data, vendor control write/read loopback, disable while requests are active, UDCs with and without isochronous endpoints, and module init/exit registering both SourceSink and loopback functions.
