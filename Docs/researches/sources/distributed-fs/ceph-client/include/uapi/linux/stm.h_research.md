# sources/distributed-fs/ceph-client/include/uapi/linux/stm.h

## Purpose
Defines userspace ioctls for the System Trace Module class, used to allocate STP master/channel ranges and set STM options.

## Important APIs, Types, and Constants
`STP_MASTER_MAX` and `STP_CHANNEL_MAX` cap values. `struct stp_policy_id` carries variable-length policy identity data with total `size`, assigned `master`, assigned `channel`, requested/returned `width`, reserved fields, and flexible `id[]`. Ioctls are `STP_POLICY_ID_SET`, `STP_POLICY_ID_GET`, and `STP_SET_OPTIONS`.

## Control Flow, State, and Persistence
Userspace passes an ID and desired channel width; the kernel fills assignment fields. Policy assignment and options live in STM class/device state, not in the header.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and ioctl definitions. Integrates with STM character devices and tracing infrastructure based on MIPI STPv2.

## Risks and Test Signals
Risks include incorrect `size` calculation for `id[]`, uninitialized reserved fields, and invalid channel width. Test variable-length ioctl handling, get-after-set behavior, maximum master/channel boundary values, and 32/64-bit struct layout.
