# sources/distributed-fs/openafs/src/rx/UKERNEL/rx_kcommon.h

Purpose: common Rx "kernel" header for the user-space kernel emulation build.

Important APIs/types/functions: includes AFS sys/user headers, Rx globals, `rx_kmutex.h`, locks, stats; declares `usr_ifnet`, `usr_in_ifaddr`, `inetdomain`, `udp_protosw`, `rxk_ports`, and `rxk_portRocks`; defines `MAXRXPORTS`, `rxk_ports_t`, `rxk_portRocks_t`, `rx_ifaddr_t`, and `rx_ifnet_t`.

Control flow: no runtime code; establishes common types and globals for UKERNEL Rx networking.

State/persistence: declared global user-mode network interface and Rx port tables.

Dependencies/integration: UKERNEL networking files, Rx globals, AFS stats, and OPR lock-backed mutex header.

Risks: duplicate includes are harmless but noisy; type aliases must match the user-mode network emulation structs. Test signals are UKERNEL compile and Rx listener initialization.
