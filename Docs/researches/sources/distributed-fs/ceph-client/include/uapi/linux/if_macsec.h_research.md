
# sources/distributed-fs/ceph-client/include/uapi/linux/if_macsec.h

## Purpose

`if_macsec.h` defines the generic-netlink UAPI for configuring and dumping MACsec devices, secure channels, secure associations, offload mode, cipher IDs, key sizes, ICV lengths, commands, and statistics. The complete 194-line file was read.

## Important APIs, Types, and Functions

Important constants include `MACSEC_GENL_NAME`, `MACSEC_GENL_VERSION`, key/key-id/salt lengths, MACsec GCM AES cipher IDs, and min/std/max ICV lengths. Enums define `macsec_attrs`, `macsec_secy_attrs`, `macsec_rxsc_attrs`, `macsec_sa_attrs`, `macsec_offload_attrs`, `macsec_nl_commands`, and RXSC/SA/TXSC/SecY stats attribute families. There are no C functions.

## Control Flow

The header defines message shape rather than flow. User space sends MACsec generic-netlink commands such as add/delete/update RXSC/TXSA/RXSA or update offload; kernel MACsec code validates nested attributes and mutates the target MACsec netdevice; dumps return nested SecY, SC, SA, and stats attributes.

## State and Persistence Behavior

Configured state lives in kernel MACsec SecY, RXSC, TXSC, and SA objects. Keys, packet numbers, replay windows, validation/encryption/protection flags, XPN salt/SSCI, and offload type persist with the MACsec device until changed or deleted.

## Dependencies and Integration Points

It includes `linux/types.h` and integrates with generic netlink, rtnetlink-created MACsec devices, IEEE 802.1AE crypto handling, hardware offload code, and user tools such as `ip macsec`.

## Risks and Edge Cases

Sensitive key material passes through `MACSEC_SA_ATTR_KEY`. Edge risks include XPN PN width differences, strict ICV length bounds, replay-window validation, offload type disagreement with hardware, and keeping stats attributes consistently 32-bit or 64-bit as documented.

## Test Signals

MACsec selftests should cover add/update/delete flows, XPN and non-XPN SAs, replay-protect validation, dumps with all nested stats, invalid key/ICV lengths, and hardware-offload negotiation failures.
