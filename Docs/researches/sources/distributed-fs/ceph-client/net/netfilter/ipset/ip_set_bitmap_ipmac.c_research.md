# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_bitmap_ipmac.c

## Purpose

`ip_set_bitmap_ipmac.c` implements the `bitmap:ip,mac` set type for IPv4 address and Ethernet MAC pairs over a bounded IPv4 range. It supports a learning-style mode where an IP can be added without a MAC and later completed from packet data.

## Important APIs And Types

The module registers `bitmap_ipmac_type` with name `bitmap:ip,mac`, features `IPSET_TYPE_IP | IPSET_TYPE_MAC`, dimension two, family IPv4, and revisions 0 through 3. `struct bitmap_ipmac` stores the member bitmap, range bounds, element count, memory size, GC timer, set backpointer, and extension storage. `struct bitmap_ipmac_elem` stores `ether[ETH_ALEN]` plus a `filled` state. `MAC_UNSET` means the element exists without a MAC; `MAC_FILLED` means the MAC is known.

`IP_SET_BITMAP_STORED_TIMEOUT` changes generic timeout behavior so an unset-MAC element can store a plain timeout value without starting an active timeout until the MAC is filled.

## Control Flow

Creation parses an IPv4 range or CIDR, rejects ranges larger than `IPSET_BITMAP_MAX_RANGE + 1`, computes an extension layout that includes `struct bitmap_ipmac_elem`, allocates map storage and bitmap, and starts GC when timeout is configured. `ip_to_id` maps an IP directly to `ip - first_ip`.

Kernel ADT validates the skb has an Ethernet device and MAC header, chooses source or destination MAC based on dimension flags, rejects zero MACs, maps the IPv4 address to an ID, and dispatches. Userspace ADT requires an IP and optionally accepts an Ethernet address. If no MAC is provided, add stores a placeholder. Test against a placeholder returns `-EAGAIN`, which the core interprets on packet path as a request to complete the element by performing an add.

The add callback handles four cases: existing filled element, existing unfilled element completed by a MAC, new filled element, and new unfilled element. When replacing a MAC under `IPSET_FLAG_EXIST`, it clears the membership bit before copying because MAC copying is not atomic, then sets the bit through the generic path.

## State And Persistence

State is the range bitmap plus per-entry MAC/fill status and extensions. Timeout values may be inactive plain values for `MAC_UNSET` entries and active jiffies timeouts for `MAC_FILLED` entries. GC only checks filled entries. There is no disk persistence.

## Dependencies And Integration

The module depends on Ethernet header helpers, ARP hardware type constants, IPv4 address extraction, netlink binary attributes, the bitmap template, and ipset core extension functions. It integrates with xtables/nftables packet matching for automatic MAC completion.

## Risks

The special partial-entry state is the main risk. Races around non-atomic MAC updates are mitigated with bit clearing and memory barriers, but changes must preserve that ordering. Timeout semantics differ before and after MAC fill. Packet path operation depends on valid Ethernet headers, so non-Ethernet devices and malformed skbs should fail cleanly. Zero MAC rejection prevents ambiguous elements.

## Test Signals

Test create/add/test/list/delete for IP-only placeholders, IP+MAC entries, timeout completion, `-exist` MAC replacement, source and destination MAC matching, invalid Ethernet attribute lengths, zero MACs, non-Ethernet skb paths, expired filled entries, and list output for unset versus filled entries.
