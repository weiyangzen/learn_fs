<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gsmmux.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/gsmmux.h

## Purpose
`gsmmux.h` defines the userspace ioctl ABI for configuring the `n_gsm` line discipline used by GSM 07.10/TS 27.010 multiplexing. It covers basic mux parameters, raw-IP network mode, extended keepalive/wait settings, and per-DLCI configuration.

## Important APIs, types, and functions
The flag `GSM_FL_RESTART` can force a DLCI reset. `struct gsm_config` carries basic line discipline settings such as adaption, encapsulation, initiator mode, timers `t1`/`t2`/`t3`, retransmit count `n2`, MRU/MTU, window `k`, and frame type `i`. `struct gsm_netconfig` configures raw-IP network interfaces. `struct gsm_config_ext` adds keepalive, wait-config, and flags. `struct gsm_dlci_config` configures channel, adaption, MTU, priority, frame type, window, and flags. Ioctls include `GSMIOC_GETCONF`, `GSMIOC_SETCONF`, `GSMIOC_ENABLE_NET`, `GSMIOC_DISABLE_NET`, `GSMIOC_GETFIRST`, `GSMIOC_GETCONF_EXT`, `GSMIOC_SETCONF_EXT`, `GSMIOC_GETCONF_DLCI`, and `GSMIOC_SETCONF_DLCI`.

## Control flow
Users attach `n_gsm` to a tty, set mux configuration, optionally create virtual tty channels or a network interface, then tune global or DLCI-specific parameters. DLCI config uses the `channel` field to select which virtual channel is being read or updated.

## State and persistence behavior
Configuration is live per line discipline instance and per DLCI. Network mode creates kernel netdevice state. Restart flags are consumed by the kernel and cleared on retrieval.

## Dependencies and integration points
It depends on `<linux/const.h>`, `<linux/if.h>`, `<linux/ioctl.h>`, and `<linux/types.h>`. It integrates with tty line disciplines, GSM modem control channels, virtual ttys, and raw-IP cellular network interfaces.

## Risks and test signals
Risks include invalid timer units, stale DLCI settings, restart side effects, unsupported protocols beyond `ETH_P_IP`, uninitialized reserved fields, and interface-name truncation. Test signals include mux setup/teardown tests, DLCI open/close resets, raw-IP netdevice creation, keepalive timeout behavior, and ABI checks for zeroed reserved fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gsmmux.h -->
