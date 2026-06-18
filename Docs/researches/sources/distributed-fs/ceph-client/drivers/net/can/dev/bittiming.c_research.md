# sources/distributed-fs/ceph-client/drivers/net/can/dev/bittiming.c

Purpose: validation and fixup for SocketCAN bit timing supplied through netlink or driver constants.

Important APIs and functions: `can_sjw_set_default()` derives a default SJW from phase segment values; `can_sjw_check()` validates SJW against controller limits and phase segments; `can_get_bittiming()` selects calculation from bitrate, direct timing fixup from time quantum, or validation against fixed bitrate tables. `can_validate_pwm_bittiming()` validates CAN XL PWM symbol timing against nominal and XL data bit times.

Control flow and state: direct timing flow checks segment ranges, sets SJW, computes BRP from clock frequency and TQ, validates BRP, and derives realized bitrate/sample point/TQ. No persistent state is stored except modifications to the passed `struct can_bittiming` or PWM validation result. Dependencies include `struct can_priv`, `can_calc_bittiming()`, netlink extack messages, and CAN XL timing helpers. Risks include rounding behavior in BRP calculation, mutation of user-provided timing fields by drivers, and consistency across FD/XL timing paths. Test signals include extack strings for invalid SJW, segment, BRP, fixed bitrate, and PWM constraints; iproute2 `ip link set canX type can ...` exercises the path.
