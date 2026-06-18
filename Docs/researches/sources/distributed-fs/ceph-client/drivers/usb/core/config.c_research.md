# Research: sources/distributed-fs/ceph-client/drivers/usb/core/config.c

Purpose: retrieves, validates, normalizes, stores, and frees USB configuration and BOS descriptors. It turns raw descriptors into `usb_host_config`, `usb_interface_cache`, `usb_host_interface`, and `usb_host_endpoint` structures used by driver binding, endpoint lookup, sysfs, usbfs, and HCD scheduling.

Important APIs and functions: public functions are `usb_get_configuration`, `usb_destroy_configuration`, `usb_release_interface_cache`, `usb_get_bos_descriptor`, and `usb_release_bos_descriptor`. Internal parsers include `usb_parse_configuration`, `usb_parse_interface`, `usb_parse_endpoint`, `usb_parse_ss_endpoint_companion`, `usb_parse_ssp_isoc_endpoint_companion`, `usb_parse_eusb2_isoc_endpoint_companion`, duplicate endpoint checks, and descriptor scanning helpers.

Control flow: `usb_get_configuration` bounds the device's configuration count, allocates config/raw descriptor arrays, reads each config header to learn `wTotalLength`, reads the full descriptor, and calls `usb_parse_configuration`. The parser validates descriptor lengths, counts interfaces/altsettings, stores IADs, allocates interface caches, then parses interfaces and endpoints. Endpoint parsing fixes invalid address bits, filters duplicate or ignored endpoints, adjusts `bInterval`, coerces low-speed bulk endpoints to interrupt, validates maxpacket sizes, handles high-speed and SuperSpeed companion descriptors, and stores class/vendor extra descriptors. BOS parsing reads the BOS header and complete set, validates each device capability length, and stores pointers to recognized capabilities.

State and persistence: descriptor state is cached in `dev->config`, `dev->rawdescriptors`, and `dev->bos`; no disk persistence. Interface caches use krefs because interfaces share altsetting cache data. Raw descriptor buffers remain for usbfs reads.

Dependencies and integration points: depends on USB descriptor definitions, HCD/device helpers, quirk flags, endian conversion, allocation helpers, and device logging. It is called during enumeration and reset/reinit paths and feeds the rest of usbcore.

Risks: descriptor parsing is an attack surface because devices control descriptor bytes. Length checks, hard limits (`USB_MAXCONFIG`, `USB_MAXALTSETTING`, `USB_MAXINTERFACES`, `USB_MAXENDPOINTS`, `USB_MAXIADS`), and quirk handling are critical. Error unwinding must free partially allocated caches. Normalizing descriptors changes what drivers see, so compatibility quirks need regression coverage. BOS capability pointers reference the allocated BOS buffer and become invalid after release.

Test signals: fuzz malformed descriptors, short descriptors, zero configs, too many configs/interfaces/altsettings/endpoints/IADs, duplicate endpoints, invalid intervals/maxpacket values, SuperSpeed and SSP companions, eUSB2 isoc companions, quirk flags, BOS truncation/unknown caps, and destroy/reparse paths under kmemleak/KASAN.
