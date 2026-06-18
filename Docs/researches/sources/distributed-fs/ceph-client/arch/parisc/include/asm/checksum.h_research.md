# sources/distributed-fs/ceph-client/arch/parisc/include/asm/checksum.h

Purpose: provides PA-RISC network checksum helpers for IPv4/IPv6 pseudo-header checksums while delegating the rest to generic checksum code.

Important APIs/types/functions: defines `csum_tcpudp_nofold`, `_HAVE_ARCH_IPV6_CSUM`, and `csum_ipv6_magic()`.

Control flow: networking code calls these inline helpers while constructing or validating TCP/UDP checksums; the helpers add source/destination addresses, length, protocol, and partial checksum without folding until the caller needs it.

State and persistence: stateless arithmetic over packet fields. Dependencies and integration: includes `linux/in6.h` and `asm-generic/checksum.h`, and integrates with the IP, TCP, UDP, and IPv6 stacks.

Risks and test signals: endian or carry-folding mistakes cause dropped packets. Test with IPv4/IPv6 TCP/UDP checksum validation, offload-disabled network tests, and packet captures on PA-RISC big-endian systems.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
