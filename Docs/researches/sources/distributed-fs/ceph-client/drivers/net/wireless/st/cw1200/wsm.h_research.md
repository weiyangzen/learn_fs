# sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/wsm.h

Purpose: Defines the CW1200 WSM firmware ABI used by the driver: command/response IDs, MIB IDs, status bits, packed request/response structs, inline MIB helpers, TX/RX message headers, queue mappings, and command-buffer structures.

Important APIs, types, and functions: Key exported structs include `wsm_hdr`, `wsm_startup_ind`, `wsm_configuration`, `wsm_scan`, `wsm_tx`, `wsm_rx`, `wsm_join`, `wsm_set_pm`, `wsm_add_key`, `wsm_edca_params`, `wsm_update_ie`, `wsm_cmd`, and `wsm_buf`. Inline helpers wrap MIBs for output power, beacon wakeup, counters, station id, RX filter, beacon filter, operational mode, template frames, protected management, block ack, association mode, retry policy, filters, keepalive, multicast, ARP, P2P PS, UAPSD, and internal TX rate. Public APIs cover WSM command calls, TX locking, RX handling, and TX buffer retrieval.

Control flow: The header encodes the firmware contract consumed by `wsm.c` and higher layers. Command structs are caller-filled, marshaled by `wsm.c`, and confirmed by firmware response IDs. Inline helpers turn typed configuration into `wsm_read_mib`/`wsm_write_mib` calls. Queue mapping helpers translate Linux VO/VI/BE/BK to firmware BE/BK/VI/VO ordering.

State and persistence: Defines in-memory command state (`struct wsm_cmd`) and dynamic command buffer (`struct wsm_buf`). MIB writes change firmware runtime state; no host persistence is declared.

Dependencies and integration points: Depends on Linux spinlocks, skbs, Ethernet constants, endian types, and `struct cw1200_common`. It is the shared contract for cw1200 TX/RX, STA, scan, AP, and BH code.

Risks: The ABI is densely packed and endian-sensitive. Several helpers compute variable payload sizes from caller-provided counts and assume bounds were already checked. `wsm_set_template_frame()` mutates skb headroom temporarily. Queue mapping arrays have no runtime bounds checking.

Test signals: Build with sparse/endian checking, exercise every MIB helper used by STA/AP setup, verify packed struct sizes against firmware spec, and test queue mapping/rate-policy MIB upload.
