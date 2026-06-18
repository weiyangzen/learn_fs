# sources/distributed-fs/ceph-client/drivers/net/can/dev/length.c

Purpose: CAN FD DLC/length conversion helpers and rough on-wire frame length estimation for BQL/statistics.

Important APIs and functions: `can_fd_dlc2len()` maps the 4-bit CAN FD DLC field to canonical payload length. `can_fd_len2dlc()` maps sanitized payload lengths back to DLC, capping oversized inputs. `can_skb_get_frame_len()` estimates frame length in bytes for CAN or CAN FD SKBs, excluding RTR payload and using `can_frame_bytes()`.

Control flow and state: no persistent state exists; static lookup tables drive conversions. The BQL helper inspects skb protocol shape through `can_is_canfd_skb()`, EFF flag, RTR flag, and payload length. Dependencies include CAN frame layout helpers and exported symbols used by CAN drivers and echo SKB accounting. Risks are table correctness for non-linear CAN FD lengths and the deliberate approximation that ignores bit stuffing and separate CAN FD BRS bitrate. Test signals include boundary conversions for lengths 0, 8, 9, 12, 64, invalid lengths above 64, RTR frames, and FD/EFF frame byte estimates.
