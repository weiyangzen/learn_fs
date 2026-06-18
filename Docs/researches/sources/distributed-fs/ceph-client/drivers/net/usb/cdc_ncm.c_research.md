# sources/distributed-fs/ceph-client/drivers/net/usb/cdc_ncm.c

## Purpose

`cdc_ncm.c` is the CDC Network Control Model host driver and the shared NCM framing engine used by MBIM. It negotiates NCM/MBIM descriptors, data altsettings, NTB parameters, 16-bit or 32-bit NTB formats, RX/TX maximums, datagram sizes, alignment rules, coalescing timers, sysfs tuning knobs, ethtool stats, notification handling, and multi-packet RX/TX framing.

## Important APIs, types, and functions

The main state is `struct cdc_ncm_ctx` from the CDC NCM header, stored in `dev->data[0]`. This file exports `cdc_ncm_change_mtu()`, `cdc_ncm_bind_common()`, `cdc_ncm_unbind()`, `cdc_ncm_select_altsetting()`, `cdc_ncm_fill_tx_frame()`, `cdc_ncm_tx_fixup()`, RX verifier helpers for NTH/NDP16/NTH/NDP32, and `cdc_ncm_rx_fixup()`. It defines sysfs attributes under `cdc_ncm`, ethtool stats for NTB reasons/overhead/counts, and `driver_info` variants for generic NCM, ZLP devices, Apple tethering/private modes, and WWAN/no-ARP devices.

## Control flow

Bind allocates the context, initializes the hrtimer/tasklet/lock, parses CDC descriptors, locates the data interface via union or IAD fallback, validates NCM/ECM or MBIM descriptors, claims the data interface, sets or avoids data altsetting toggles based on quirk flags, issues `GET_NTB_PARAMETERS`, optionally disables CRC mode, selects NTB16 or NTB32, initializes TX/RX limits and alignment values, waits briefly for firmware, activates the data altsetting, discovers endpoints on data/control interfaces, reads the MAC address when available, performs NCM setup, allocates delayed NDP storage for NDP-to-end devices, installs ethtool/sysfs/netdev ops, and sets max MTU.

TX uses `cdc_ncm_tx_fixup()` and `cdc_ncm_fill_tx_frame()` to coalesce Ethernet datagrams into an NTB until the NTB is full, the NDP is full, max datagrams are reached, a timer expires, or an explicit flush occurs. It builds NTH16/NTH32 headers, chains or delays NDPs, aligns payloads, handles low-memory fallback by shrinking NTB allocation, pads or forces short packets, updates private overhead counters, and adjusts usbnet TX stats to count payload bytes. A high-resolution timer schedules a tasklet that flushes pending frames through `usbnet_start_xmit(NULL, dev->net)`.

RX verifies the NTH signature, block length, and sequence number, verifies NDP size and bounds, checks NDP signatures, iterates datagram entries until the first null entry, validates offset/length against the SKB and `rx_max`, copies each Ethernet frame into a fresh SKB, and returns it. CDC notifications update carrier and speed, including split speed-change data. `cdc_ncm_update_filter()` delegates CDC packet filter programming only if the device advertises filtering support.

## State and persistence

Runtime state includes negotiated NCM parameters, RX/TX max sizes, max datagram size, NDP format, TX coalescing SKBs, delayed NDP buffers, timer state, stop flag, sequence counters, stats, quirk flags, and sysfs-configurable values. No disk persistence exists. Device state is programmed through CDC class requests for NTB input size, NTB format, CRC mode, and max datagram size.

## Dependencies and integration points

The driver depends on `usbnet`, USB CDC descriptors and class requests, hrtimers, tasklets, ethtool, sysfs groups, MII/link helpers, CRC/ethernet helpers, and exported `usbnet_cdc_update_filter()` from `cdc_ether.c`. `cdc_mbim.c` depends on its exported bind/framing/RX verification helpers.

## Risks

High-risk areas are descriptor compatibility, NTB bounds verification, NDP chaining, low-memory TX fallback, timer/tasklet flushing races, and sysfs changes while the netdev is running. The code uses locks around TX context mutation and cancels timer/tasklet on unbind. Product matching order matters because MBIM-compatible NCM functions may be rejected here so `cdc_mbim` can bind when preferred.

## Test signals

Test NTB16 and NTB32 devices, generic and ZLP variants, Apple interfaces, WWAN/no-ARP IDs, MBIM preference rejection, descriptor fallback through IAD, RX malformed NTH/NDP cases, multi-NDP chains, TX coalescing timeout/full/max-datagram reasons, sysfs changes to `rx_max`, `tx_max`, `tx_timer_usecs`, `ndp_to_end`, MTU changes, suspend/resume, and CDC notification speed/carrier handling.
