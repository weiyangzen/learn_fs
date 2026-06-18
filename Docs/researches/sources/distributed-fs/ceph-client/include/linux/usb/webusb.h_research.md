# sources/distributed-fs/ceph-client/include/linux/usb/webusb.h

## Purpose
This header defines WebUSB platform capability and URL descriptor constants for USB gadget/device code exposing WebUSB metadata.

## Important APIs, types, and functions
Important items are `WEBUSB_UUID`, `usb_webusb_cap_data`, `WEBUSB_VERSION_1_00`, landing-page presence constants, `WEBUSB_GET_URL`, `webusb_url_descriptor`, URL scheme constants, header lengths, and `WEBUSB_URL_RAW_MAX_LENGTH`.

## Control flow, state, and persistence
Gadget code advertises the platform capability in BOS descriptors and answers vendor requests for URL descriptors. State is descriptor data configured by the gadget; the header only defines wire layout and limits.

## Dependencies and integration points
It depends on USB chapter 9 UAPI definitions and little-endian conversion. It integrates with USB gadget BOS descriptor construction and browser/user-agent WebUSB discovery.

## Risks and test signals
Risks include malformed descriptor lengths, invalid URL scheme values, landing-page index mismatches, and exceeding one-byte descriptor length limits. Tests should inspect generated BOS/URL descriptors and issue GET_URL requests with valid and invalid indexes.
