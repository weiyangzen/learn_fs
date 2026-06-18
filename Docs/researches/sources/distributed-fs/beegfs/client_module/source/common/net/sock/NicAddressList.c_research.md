# sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressList.c

Purpose: Implements equality comparison for BeeGFS NIC address lists.

Important APIs/types/functions: `NicAddressList_equals` first compares list length, then walks both underlying `PointerList` instances in order and calls `NicAddress_equals` for each pair.

Control flow: The function returns false on different lengths, otherwise remains true only while every aligned element matches. Order is significant; it is not a set comparison.

State and persistence behavior: Read-only traversal of caller-owned lists; no allocations or persistence.

Dependencies and integration points: Depends on `PointerListIter`, `NicAddress_equals`, and the list wrapper declared in `NicAddressList.h`.

Risks: Because order matters, discovery-order changes can make equivalent address sets compare different. Null element handling is not defensive.

Test signals: Equal lists, length mismatch, same entries in different order, and entries differing by IP/type/name.
