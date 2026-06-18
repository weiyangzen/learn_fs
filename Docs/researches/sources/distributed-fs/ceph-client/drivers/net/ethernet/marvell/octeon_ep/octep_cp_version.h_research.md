# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_cp_version.h Research

## Purpose
`octep_cp_version.h` defines the packed integer encoding used for Octeon EP control-plane protocol versions.

## Important APIs, Types, And Functions
The only public macro is `OCTEP_CP_VERSION(a, b, c)`, which packs three 8-bit version components into a 24-bit value with major in bits 23:16, minor in bits 15:8, and patch in bits 7:0.

## Control Flow
There is no control flow. The macro is used as a comparable integer by control-net version gates.

## State, Persistence, And Dependencies
The header owns no state. Its output values are stored in `octep_ctrl_mbox.version` and command-version tables in `octep_ctrl_net.c`.

## Integration Points
`octep_ctrl_net.h` includes this header, and `octep_ctrl_net.c` uses it to define `OCTEP_CP_VERSION_CURRENT` and minimum command versions for host-to-firmware and firmware-to-host commands.

## Risks
Each component is masked to 8 bits, so values above 255 wrap silently. Integer ordering works for major/minor/patch comparisons only while this packed format remains consistent across host and firmware. The file uses a BSD-3-Clause SPDX line while most local driver files are GPL-2.0, so license compatibility should remain intentional.

## Test Signals
Compile protocol users and validate version negotiation with firmware minimum and maximum versions, especially for commands added after 1.0.0 such as offload configuration.
