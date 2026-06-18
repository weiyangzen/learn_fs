# sources/distributed-fs/ceph-client/include/net/rpl.h

Purpose: declares IPv6 RPL lightweight tunnel init/exit hooks and source-routing header compression/decompression helpers.

Important APIs and types: when `CONFIG_IPV6_RPL_LWTUNNEL` is enabled, `rpl_init()` and `rpl_exit()` are external; otherwise init succeeds and exit is a no-op. `ipv6_rpl_srh_decompress()` and `ipv6_rpl_srh_compress()` convert RPL source routing headers relative to destination address and address count.

Control flow: IPv6 tunnel/module init calls RPL init/exit conditionally; packet processing compresses/decompresses SRH fields for RPL routing.

State and persistence: no state in the header; RPL tunnel registration state lives in implementation.

Dependencies and integration points: depends on Linux RPL UAPI and IPv6 lightweight tunnel support.

Risks and test signals: risks include config stubs hiding missing registration, SRH compression length errors, and destination-address reconstruction mistakes. Test enabled/disabled builds, RPL LWT setup, compress/decompress round trips, and malformed SRH lengths.
