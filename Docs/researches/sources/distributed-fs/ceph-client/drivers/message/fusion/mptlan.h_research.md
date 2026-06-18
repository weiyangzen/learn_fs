# sources/distributed-fs/ceph-client/drivers/message/fusion/mptlan.h

## Purpose
`mptlan.h` is the local header for the Fusion MPT IP-over-FC network driver. It includes the kernel networking and MPT base dependencies, defines module metadata, LAN queue/MTU constants, reset resource flags, debug print wrappers, and helper macros for converting netdevs to private adapter state.

## Important APIs, Types, and Functions
Key constants are `MPT_LAN_MAX_BUCKETS_OUT`, `MPT_LAN_BUCKET_THRESH`, `MPT_LAN_BUCKETS_REMAIN_MISMATCH_THRESH`, `MPT_LAN_RX_COPYBREAK`, `MPT_LAN_TX_TIMEOUT`, `MPT_TX_MAX_OUT_LIM`, `MPT_LAN_MIN_MTU`, `MPT_LAN_MAX_MTU`, `MPT_LAN_MTU`, `MPT_LAN_NAA_RFC2625`, `MPT_LAN_NAA_QLOGIC`, and reset resource flags for returning posted buckets and pending transmits. Helper macros include `dioprintk`, `dlprintk`, `NETDEV_TO_LANPRIV_PTR`, `NETDEV_PTR_TO_IOC_NAME_s`, and `IOC_AND_NETDEV_NAMES_s_s`.

## Control Flow
`mptlan.c` includes this header first to pull in Linux networking primitives and `mptbase.h`. Compile-time debug symbols choose whether IO and LAN debug macros emit `printk()` calls or compile to `no_printk()`. Runtime code uses the netdev helper macros in log statements and adapter lookups.

## State and Persistence
The header defines constants and macros only. Persistent state is allocated in `struct mpt_lan_priv` inside `mptlan.c`; this header constrains that state through queue limits, MTU bounds, and timeout settings.

## Dependencies and Integration Points
It integrates the LAN driver with Linux module, netdevice, FC device, skbuff, ARP hardware type, workqueue, delay, uaccess, IO, and the Fusion base header. The MTU defaults follow RFC2625 IP-over-FC sizing.

## Risks and Edge Cases
Changing queue constants can break firmware assumptions about maximum buckets and transaction contexts. The debug macros are compile-time only and do not honor `mptdebug.h` runtime categories. Helper macros assume `netdev_priv()` is a valid `mpt_lan_priv`, so they are unsafe for unrelated netdevs.

## Test Signals
Compile coverage should verify the header works with `mptlan.c` and that debug symbols on/off build cleanly. Runtime tests should verify default MTU, min/max MTU enforcement, watchdog timeout, and log helper paths through normal open, TX/RX, reset, and close.
