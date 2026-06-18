# `sources/distributed-fs/ceph-client/include/linux/usb/rndis_host.h`

## Purpose

`rndis_host.h` defines Remote NDIS message layouts and host-side helper declarations for USB RNDIS networking. It includes control/data message structures, timeouts, default packet filters, driver-data flags, and usbnet integration functions.

## Important APIs, Types, and Constants

- Packed/little-endian message structs cover message header, data packets, initialize/complete, halt, query/complete, set/complete, reset/complete, indicate status, keepalive, and keepalive complete.
- `CONTROL_BUFFER_SIZE` and `RNDIS_CONTROL_TIMEOUT_MS` define control exchange sizing and timeout.
- `RNDIS_DEFAULT_FILTER` selects directed, broadcast, all multicast, and promiscuous-related packet filters as defined in the header.
- Driver flags describe physical-medium assumptions, polling status before control, and destination-MAC fixup behavior.
- Exported helpers include `rndis_status()`, `rndis_command()`, `generic_rndis_bind()`, `rndis_unbind()`, `rndis_rx_fixup()`, and `rndis_tx_fixup()`.

## Control Flow and Lifetimes

During bind, usbnet RNDIS code initializes the device with control messages, queries capabilities, sets packet filters, and opens data endpoints. RX fixup strips RNDIS data headers and validates offsets/lengths before handing packets to networking. TX fixup wraps sk_buffs in RNDIS data headers. Status URBs deliver unsolicited indications and keepalive/status events.

## State and Persistence Behavior

Wire messages are transient. usbnet device state stores negotiated parameters, flags, filters, MAC handling, and endpoint URBs for the interface lifetime. No disk persistence exists.

## Dependencies and Integration Points

It depends on USB networking (`usbnet`), URBs, sk_buffs, and little-endian wire fields. It integrates CDC/RNDIS USB devices with Linux netdev and usbnet generic bind/unbind paths.

## Risks and Edge Cases

RNDIS devices are often non-compliant. Header offsets and lengths must be validated to avoid skb overreads. Control commands can time out or require polling. Some devices ignore configured MAC addresses. Reset/indicate/keepalive messages may arrive asynchronously with disconnect.

## Test Signals

Bind several RNDIS devices, test init/query/set/reset/keepalive exchanges, RX/TX fixups with malformed lengths, control timeout handling, MAC fixup devices, suspend/resume, unplug during control command, and netdev traffic under stress.
