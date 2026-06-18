<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/cdc.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/cdc.h

Purpose: provides kernel CDC helper declarations and a parsed-header aggregate for USB Communications Device Class functional descriptors.

Important APIs and types: `CDC_PHONET_MAGIC_NUMBER` names a nonstandard marker. `struct usb_cdc_parsed_header` stores pointers to parsed CDC union, header, call-management, ACM, country, network terminal, Ethernet, DMM, MDLM, MDLM detail, OBEX, NCM, MBIM, and MBIM extended descriptors plus a Phonet magic flag. `cdc_parse_cdc_header()` parses raw descriptor bytes from an interface.

Control flow: CDC class drivers pass an interface and descriptor buffer to `cdc_parse_cdc_header()`, then inspect the aggregate to select ACM/NCM/MBIM/Ethernet behavior and locate companion interfaces/endpoints.

State and persistence: parsed pointers refer into descriptor memory owned by usbcore; no independent storage is owned here.

Dependencies and integration points: includes CDC UAPI definitions and forward-declares `struct usb_interface`. It integrates with USB serial, network, modem, and WWAN CDC drivers.

Risks and test signals: risks include duplicate descriptors, malformed lengths, stale pointers if descriptor storage lifetime is misunderstood, and ambiguous vendor-specific CDC layouts. Test parsing of ACM/NCM/MBIM devices, descriptor fuzzing, Phonet quirks, and multi-interface union descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/cdc.h -->
