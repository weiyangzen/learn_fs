## sources/distributed-fs/ceph-client/include/linux/can/bittiming.h

**Purpose:** This header defines CAN bit-timing, CAN FD/XL transmission-delay compensation, PWM timing, and calculation/validation interfaces for CAN network drivers.

**Important APIs/types/functions:** Constants include `CAN_SYNC_SEG`, unset/unknown bitrate sentinels, and TDC ctrlmode masks. Types include `struct can_tdc`, `can_tdc_const`, `can_pwm`, `can_pwm_const`, and `data_bittiming_params`. APIs include config-gated `can_calc_bittiming()`, `can_calc_tdco()`, `can_calc_pwm()`, plus `can_sjw_set_default()`, `can_sjw_check()`, `can_get_bittiming()`, `can_validate_pwm_bittiming()`, and inline helpers `can_get_relative_tdco()`, `can_bit_time()`, `can_bit_time_tqmin()`, and `can_tqmin_to_ns()`.

**Control flow, state, persistence:** Calculation helpers fill driver-owned timing structures from requested bitrate/sample-point constraints. If `CONFIG_CAN_CALC_BITTIMING` is absent, calculation stubs report `-EINVAL` through netlink extack. Timing state persists in `struct can_priv` fields.

**Dependencies/integration:** Depends on netdevice and CAN netlink UAPI. Integrated by CAN drivers during netlink configuration and device open/reconfigure paths.

**Risks and test signals:** Risks include invalid segment limits, mixing absolute and relative TDCO semantics, failing to respect ctrlmode support, and config-disabled behavior not surfaced to users. Test signals include iproute2 bitrate configuration, extack messages, CAN FD/XL TDC cases, PWM validation, and hardware loopback at configured rates.
