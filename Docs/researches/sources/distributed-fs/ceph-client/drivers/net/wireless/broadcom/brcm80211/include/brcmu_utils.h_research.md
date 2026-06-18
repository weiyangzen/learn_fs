# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/brcmu_utils.h

Purpose: Declares shared Broadcom utility macros, packet queue structures/APIs, bitfield helpers, debug helpers, and revision string helpers.

Important APIs/types: Provides `SPINWAIT`, packet queue constants, bit-array macros (`setbit`, `clrbit`, `isset`, `isclr`), bit mask macros, CRC constants, `struct pktq_prec`, `struct pktq`, inline queue inspection helpers, packet buffer APIs, queue enqueue/dequeue/flush APIs, bitfield `brcmu_maskset/get{16,32}`, DEBUG conditional packet dump APIs, and buffer length constants for revision strings.

Control flow and state: Inline helpers read queue counters and update masked integer fields. Runtime state is held by caller-owned `pktq` and SKBs manipulated by `utils.c`.

Dependencies and integration: Includes Linux SKB definitions and is shared by brcmsmac/brcmfmac utility users. Risks include macro argument side effects, `SPINWAIT` requiring explicit post-condition checks, no internal locking around queues, bit macros assuming byte-addressable storage, and mask helpers expecting shifted masks. Test signals include queue operation tests, bitfield round trips, spinwait timeout behavior, DEBUG/non-DEBUG builds, and static analysis for side-effect arguments.
