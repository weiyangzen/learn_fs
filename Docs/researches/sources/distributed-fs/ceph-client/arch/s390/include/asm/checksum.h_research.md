<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/checksum.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/checksum.h

Purpose: Implements s390 IP checksum helpers.

Important APIs/types/functions: `cksm()`, `csum_fold()`, `ip_fast_csum()`, `csum_tcpudp_nofold()`, `csum_tcpudp_magic()`, `ip_compute_csum()`, and IPv6 checksum hooks. Source-visible declarations include: #define _S390_CHECKSUM_H; static inline __wsum cksm(const void *buff, int len, __wsum sum); union register_pair rp = {; #define _HAVE_ARCH_CSUM_AND_COPY; static inline __sum16 csum_fold(__wsum sum); static inline __sum16 ip_fast_csum(const void *iph, unsigned int ihl); static inline __wsum csum_tcpudp_nofold(__be32 saddr, __be32 daddr, __u32 len,; static inline __sum16 csum_tcpudp_magic(__be32 saddr, __be32 daddr, __u32 len,; static inline __sum16 ip_compute_csum(const void *buff, int len); #define _HAVE_ARCH_IPV6_CSUM.

Control flow: Inline assembly and arithmetic helpers compute Internet checksums and pseudo-header checksums, folding carries to 16-bit sums.

State and persistence behavior: No persistent state; functions consume packet/header buffers.

Dependencies and integration points: Direct includes are #include <linux/instrumented.h>, #include <linux/kmsan-checks.h>, #include <linux/in6.h>. Integrated with Integrates IPv4/IPv6, TCP/UDP, skb checksum offload fallback, and generic checksum API..

Risks: Endianness, odd lengths, carry folding, and copy-and-checksum semantics are packet-corruption sensitive.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 128 lines, 3250 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/checksum.h -->
