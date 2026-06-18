# sources/distributed-fs/ceph-client/net/netfilter/nft_osf.c

Purpose: implements nftables passive OS fingerprint expression `osf` for IPv4 TCP SYN packets, writing a genre or genre:version string to a register.

Important APIs/types/functions: `struct nft_osf` stores destination register, TTL matching mode, and flags. `nft_osf_eval()` validates IPv4, TCP, non-fragment, SYN-only packets, calls `nf_osf_find()` against `nf_osf_fingers`, and pads the result into `NFT_OSF_MAXGENRELEN`. `nft_osf_validate()` restricts use to IPv4/inet prerouting, local-in, and forward hooks.

Control flow: init requires destination register, accepts TTL values 0..2, accepts only `NFT_OSF_F_VERSION`, and validates a destination register store of the fixed OSF string length. Eval breaks for unsupported family/protocol/fragments/non-SYN or missing TCP header. If no fingerprint matches, it writes `"unknown"`; with version flag it formats genre and version, otherwise genre only. Dump emits TTL, flags, and dreg.

State/persistence: expression state is fixed metadata; fingerprint data is global OSF data outside this file. Dependencies include IPv4 and TCP header parsing, nfnetlink OSF fingerprint tables, and nf_tables register storage. Risks include IPv4-only behavior in inet tables, reliance on loaded fingerprint database, string truncation/padding, endian oddity in flags dump, and fragmented SYN handling. Test signals: known and unknown fingerprints, version flag formatting, TTL modes, non-SYN/TCP/IPv4 break behavior, fragment rejection, hook validation, fixed-length register writes, and dump/restore.
