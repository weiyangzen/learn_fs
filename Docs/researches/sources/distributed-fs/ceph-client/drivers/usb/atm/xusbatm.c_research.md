# sources/distributed-fs/ceph-client/drivers/usb/atm/xusbatm.c

## Purpose
`xusbatm.c` is a generic, parameter-driven `usbatm` mini-driver for USB DSL modems that are initialized by userspace or unsupported by specific mini-drivers. It creates up to eight dynamic USB ID and mini-driver entries from module parameters and binds endpoints/altsettings without firmware logic.

## Important APIs, Types, And Functions
- Module parameter arrays define `vendor`, `product`, `rx_endpoint`, `tx_endpoint`, `rx_padding`, `tx_padding`, `rx_altsetting`, and `tx_altsetting`.
- `xusbatm_find_intf()` locates an interface containing an endpoint in a requested altsetting.
- `xusbatm_capture_intf()` optionally claims an interface and sets its altsetting.
- `xusbatm_bind()` validates RX/TX interfaces and altsettings, claims non-primary interfaces, and configures endpoints.
- `xusbatm_unbind()` releases every interface owned by this `usbatm` instance.
- `xusbatm_atm_start()` assigns a random ESI/MAC because no hardware-specific retrieval exists.
- `xusbatm_init()` validates parameter counts and fills `xusbatm_usb_ids[]` plus `xusbatm_drivers[]`.

## Control Flow
On module load, the parameter arrays must contain equal counts for vendor, product, RX endpoint, and TX endpoint. Each entry becomes a USB device ID and a `usbatm_driver`. Probe selects the corresponding driver by ID-array offset and calls `usbatm_usb_probe()`. Bind finds RX and TX interfaces at requested altsettings, rejects unrelated primary interfaces or conflicting altsettings on the same interface, claims any companion interfaces, and returns to the core for URB setup.

## State And Persistence Behavior
Global arrays store parameter-derived USB IDs and driver descriptors for the module lifetime. Per-device state is owned by `usbatm`; this driver has no extra per-device allocation. ATM ESI is random at each start and is not persistent.

## Dependencies And Integration Points
It depends on USB core, `usbatm`, and `eth_random_addr()`. Userspace is expected to handle device-specific firmware or initialization before kernel ATM traffic is useful.

## Risks And Edge Cases
Malformed parameter arrays fail module load. Endpoint numbers are normalized by forcing RX IN and TX endpoint number bits, which can surprise users who pass full endpoint addresses. Same-interface RX/TX with different altsettings is rejected. No modem status, firmware, line control, or real MAC retrieval exists, so operational success depends on external setup.

## Test Signals
Load with valid and invalid parameter counts. Bind a test USB device with RX/TX endpoints on the same and different interfaces. Verify altsetting changes, companion interface claims/releases, random ESI assignment, and clean unbind. Confirm data paths inherit padding values through `usbatm`.
