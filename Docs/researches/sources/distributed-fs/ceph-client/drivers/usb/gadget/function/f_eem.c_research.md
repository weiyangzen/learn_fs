# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_eem.c

## Purpose
`f_eem.c` implements the USB CDC Ethernet Emulation Model function. Unlike ECM, it uses one interface with bulk IN/OUT endpoints and wraps Ethernet frames in EEM packet headers/trailers. It integrates with `u_ether` for the network device and registers a configfs function named `eem`.

## Important APIs, Types, and Functions
`struct f_eem` embeds `struct gether` and stores one interface ID. `struct in_context` tracks dynamically allocated echo-response request context. Descriptor tables include a CDC EEM communication-class interface and FS/HS/SS bulk endpoints with SuperSpeed companion descriptors. Key functions are `eem_setup()`, `eem_set_alt()`, `eem_disable()`, `eem_bind()`, `eem_wrap()`, `eem_unwrap()`, `eem_cmd_complete()`, `eem_alloc_inst()`, `eem_alloc()`, `eem_unbind()`, and `eem_free()`.

## Control Flow
Instance allocation creates `f_eem_opts`, initializes a default `u_ether` netdev, and exposes standard Ethernet configfs attributes. Function allocation increments the option refcount, sets `gether` I/O state, and installs wrap/unwrap callbacks plus header length. Bind registers or attaches the netdev, assigns a string and interface ID, autoconfigures bulk endpoints, mirrors endpoint addresses to HS/SS descriptors, assigns descriptor copies, and increments bind count. `set_alt()` only accepts alt 0 on the single interface; it disconnects any old session, configures speed-appropriate endpoints if needed, sets `is_zlp_ok` and default filter, and calls `gether_connect()`.

`eem_wrap()` prepends a two-byte EEM data header and appends an Ethernet FCS. It uses the sentinel `0xdeadbeef` CRC form and appends a zero-length EEM packet when needed to avoid USB ZLP ambiguity. `eem_unwrap()` parses one or more EEM packets from a received USB transfer. Data packets are CRC-checked, stripped of FCS, copied with `NET_IP_ALIGN`, and queued to the network receive list. Command packets handle echo by cloning the payload and queueing an IN response; other command hints are ignored.

## State and Persistence
Per-instance persistent state is primarily the `u_ether` netdev/options and endpoint descriptors assigned during bind. Runtime RX parsing state is per-skb; echo responses allocate temporary USB requests, buffers, and `in_context` freed in `eem_cmd_complete()`. No class-specific control state is accepted via EP0; `eem_setup()` always stalls unsupported control requests.

## Dependencies and Integration Points
EEM depends on `u_ether` for netdev lifecycle and data path, `u_ether_configfs.h` for configfs attributes, CRC helpers for calculated EEM CRC validation, skb helpers for frame wrapping/unwrapping, and composite helpers for descriptor/string/interface/endpoint setup. Its wrap/unwrap callbacks are consumed by `u_ether` during USB network TX/RX.

## Risks
RX parsing handles multiple logical packets per USB transfer and must keep `skb_pull()` lengths exact after errors, echo commands, zero-length packets, and invalid CRCs. Echo response allocation occurs in atomic-ish receive context but uses `GFP_KERNEL` for `req->buf`, which is worth checking against call context expectations in surrounding `u_ether`. Sentinel CRC mode is used for transmitted packets; calculated CRC receive validation must accept both forms. ZLP avoidance depends on `in->maxpacket` being configured before wrapping.

## Test Signals
Test EEM frame TX/RX at FS/HS/SS, transfers containing multiple EEM packets, zero-length EEM padding, sentinel and calculated CRC packets, invalid headers/lengths/CRCs, echo command and completion cleanup, host disconnect while echo response is queued, suspend-like command hints, and configfs Ethernet attributes.
