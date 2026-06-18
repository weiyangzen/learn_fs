# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_ncm.c

## Purpose

`f_ncm.c` implements the USB CDC Network Control Model gadget function. It presents a USB NCM Ethernet link, integrates with the `u_ether` network gadget core, wraps outgoing Ethernet frames into NCM Transfer Blocks, unwraps incoming NTBs into SKBs, and handles CDC NCM class control requests and notifications.

## Important APIs, Types, and Functions

`struct f_ncm` embeds `struct gether` and adds control/data interface IDs, host MAC string, notify endpoint/request state, NDP parser mode, CRC mode, notification lock/count, netdev pointer, multi-frame TX aggregation SKBs, datagram count, and an hrtimer. `struct ndp_parser_opts` abstracts NDP16 versus NDP32 field widths, signatures, header sizes, alignment, and field positions. Configfs state is `struct f_ncm_opts` from `u_ncm.h`, with Ethernet address/qmult/ifname helpers and local `max_segment_size`.

Key functions include `ncm_reset_values()`, `ncm_setup()` for CDC requests, `ncm_set_alt()`/`ncm_get_alt()`/`ncm_disable()` for interface activation, `ncm_notify()` and `ncm_notify_complete()` for network connection and speed notifications, `ncm_wrap_ntb()` and `package_for_tx()` for TX aggregation, `ncm_unwrap_ntb()` for RX validation and SKB extraction, `ncm_tx_timeout()` for delayed TX flush, and `ncm_bind()`/`ncm_unbind()`/`ncm_alloc()` for function lifecycle.

## Control Flow

`ncm_alloc_inst()` creates a default Ethernet netdev and configfs/OS descriptor state. `ncm_alloc()` allocates a function, exports the host MAC address string, resets NCM defaults to NDP16/no-CRC/default filters, and wires `gether` wrap/unwrap callbacks. `ncm_bind()` registers or attaches the Ethernet netdev, assigns string/interface IDs, autoconfigures bulk and interrupt endpoints, allocates the notification request, copies endpoint addresses across speeds, assigns descriptors, sets `open`/`close` callbacks, and initializes the TX hrtimer.

The control interface altsetting initializes the notification endpoint. The data interface altsetting 0 disconnects the network path; altsetting 1 configures bulk endpoints, enables ZLP policy, resets filters, calls `gether_connect()`, stores the netdev, and queues notifications. CDC requests set packet filters, get/set NTB input size, get NTB parameters, get/set NDP16/NDP32 format, and get/set CRC mode. `ncm_wrap_ntb()` aggregates outgoing frames until size, datagram-count, or timeout limits force `package_for_tx()`. `ncm_unwrap_ntb()` validates NTH/NDP signatures, lengths, indexes, optional CRCs, max segment size, and chained NTBs before queuing Ethernet SKBs to `u_ether`.

## State and Persistence Behavior

Runtime state includes selected NDP format, CRC mode, CDC packet filter, fixed NTB input/output lengths, open/closed notification state, active netdev, and partially built TX NTB SKBs. `ncm->lock` serializes notification state with open/close and completion. The hrtimer persists only until pending TX aggregation is flushed or unbound. Configfs values for addresses, qmult, interface name, and max segment size live in `f_ncm_opts` and are not persistent across teardown. The Ethernet netdev is shared across binds through the function instance and detached when bind count drops to zero.

## Dependencies and Integration Points

The driver depends on USB composite/gadget APIs, CDC/NCM descriptor definitions, Linux networking/SKB helpers, CRC32, `u_ether` and `u_ether_configfs`, `u_ncm.h`, configfs, OS descriptors, and hrtimers. It registers as `DECLARE_USB_FUNCTION_INIT(ncm, ...)`. It integrates with host CDC NCM class drivers, Linux network stack through `gether`, and Microsoft OS descriptors when the composite device enables OS strings.

## Risks and Test Signals

Risks include NTB parser boundary mistakes, CRC mode interoperability, NDP16/NDP32 switching while traffic is active, hrtimer flush invoking `ndo_start_xmit(NULL)` as a known layering compromise, notification request lifetime during disconnect/unbind, static global descriptor mutation across instances, max segment size validation and MTU interaction, and filter writes lacking full cross-CPU serialization with TX paths. The TX error path must free both aggregate SKBs and the current input SKB without leaving stale pointers.

Strong test signals include FS/HS/SS enumeration, control requests for NTB parameters/input size/format/CRC mode, invalid control-request stalls, altsetting 0/1 transitions, netdev open/close notifications, traffic with and without CRC, NDP16 and NDP32 RX/TX, chained NTBs and Windows one-byte ZLP avoidance padding, small-frame aggregation and timer flush, max_segment_size boundary tests, OS descriptor presence, bind-count attach/detach behavior, and disconnect/unbind with notification and TX timer pending.
