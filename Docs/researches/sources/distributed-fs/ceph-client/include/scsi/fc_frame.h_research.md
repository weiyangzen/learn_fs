# sources/distributed-fs/ceph-client/include/scsi/fc_frame.h

Purpose: Defines the libfc frame wrapper around `sk_buff`, receive metadata in `skb->cb`, FC ID endian helpers, frame allocation/free helpers, header/payload accessors, CRC checks, and FC header filling.

Important APIs/types/functions: `struct fc_frame` embeds an skb. `struct fcoe_rcv_info` stores local port, sequence, FCP packet, CRC, max payload, SOF/EOF, flags, encapsulation, and granted MAC. Macros expose frame fields. Helpers include `ntoh24()`, `hton24()`, `fc_frame_init()`, `fc_frame_alloc()`, `fc_frame_free()`, header/payload getters, SID/DID getters, class/rctl/cmd checks, CRC check declaration, leak check, `__fc_fill_fc_hdr()`, and `fc_fill_fc_hdr()`.

Control flow and state: Frames are allocated with FC headroom/tailroom and initialized lazily for performance; callers must eventually set header, length, SOF, and EOF. Payload access validates minimum length. Header fill writes r_ctl, DID/SID, type, F_CTL, and parameter offset.

Dependencies and integration: Depends on skb, scatterlist, SCSI command, FC protocol headers, Ethernet headers, and libfc exchange/FCP layers.

Risks and test signals: Risks include `skb->cb` size overflow, insufficient frame length checks, non-linear skb assumptions, CRC unchecked flags, and 24-bit FC ID conversion mistakes. Tests should cover allocation with unaligned payload sizes, payload bounds, header fill golden values, CRC validation, and leak detection.
