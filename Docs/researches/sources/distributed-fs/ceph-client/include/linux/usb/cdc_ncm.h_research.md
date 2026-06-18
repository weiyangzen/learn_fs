<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/cdc_ncm.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/cdc_ncm.h

Purpose: declares common state, constants, flags, and helper APIs for USB CDC Network Control Model and MBIM network transfers.

Important APIs and types: constants define NCM/MBIM alternate settings, NDP16/32 minimum lengths, default/max NTB sizes, datagram limits, timer thresholds, and driver flags. Macros identify MBIM communication/data interfaces. `struct cdc_ncm_ctx` stores parsed functional descriptors, usbnet/control/data interfaces, TX aggregation skb state, delayed NDP pointers, spinlock/stop flag, timer/tasklet, frame/datagram sizing and alignment fields, sequence numbers, and TX/RX statistics. APIs include altsetting selection, MTU change, bind/unbind, TX frame fill/fixup, RX NTH/NDP verification, and RX fixup.

Control flow: usbnet-based drivers bind through `cdc_ncm_bind_common()`, negotiate NCM parameters, collect outgoing datagrams into NTBs with timers/tasklets, verify incoming NTB headers/NDPs, split datagrams, and handle MBIM-specific alternate settings and descriptors.

State and persistence: all state is per-interface runtime state in `cdc_ncm_ctx`: active skb aggregation, timers, sequence numbers, negotiated sizes, flags, descriptor pointers, and stats. Nothing persists across disconnect.

Dependencies and integration points: depends on CDC UAPI NCM/MBIM descriptors, usbnet, net_device/sk_buff/tasklet/hrtimer/spinlock consumers in implementation, and USB interface descriptors. It integrates CDC NCM/MBIM class networking with Linux networking.

Risks and test signals: risks include NTB/NDP bounds validation, sequence handling, timer/tasklet races on disconnect, low-memory TX aggregation behavior, altsetting toggles for MBIM, MTU/max-datagram negotiation, and alignment/modulus mistakes. Test with NCM and MBIM devices, malformed NTBs, MTU changes, suspend/resume, disconnect under traffic, high-throughput aggregation stats, and packet fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/cdc_ncm.h -->
