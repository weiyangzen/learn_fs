# sources/distributed-fs/ceph-client/drivers/message/fusion/mptctl.h

## Purpose
`mptctl.h` defines the user-facing ioctl ABI for `/dev/mptctl`. It contains ioctl numbers, common headers, adapter/target/event query structures, firmware transfer structures, raw MPI pass-through structures, 32-bit compat variants, and HP/Compaq compatibility commands.

## Important APIs, Types, and Functions
Important ioctl constants include `MPTFWDOWNLOAD`, `MPTCOMMAND`, `MPTIOCINFO`, `MPTTARGETINFO`, `MPTTEST`, `MPTEVENTQUERY`, `MPTEVENTENABLE`, `MPTEVENTREPORT`, `MPTHARDRESET`, `MPTFWREPLACE`, `HP_GETHOSTINFO`, and `HP_GETTARGETINFO`. Main ABI structures are `mpt_ioctl_header`, `mpt_fw_xfer`, `mpt_ioctl_iocinfo` plus rev0/rev1 variants, `mpt_ioctl_targetinfo`, event query/enable/report structs, `mpt_ioctl_test`, `mpt_ioctl_replace_fw`, `mpt_ioctl_command`, and HP host/target info records.

## Control Flow
User space populates `mpt_ioctl_header` with IOC number, port, and maximum data size, then passes one of the `_IOWR` or `_IOR` commands to `mptctl.c`. Variable-length commands place flexible trailing arrays at the end of the structure, such as target IDs, event entries, replacement firmware bytes, or raw MPI frames.

## State and Persistence
This header defines ABI shapes rather than storage. Its fields describe data copied across the user/kernel boundary and therefore persist as a compatibility contract for existing tools. Firmware replacement and raw command buffers are caller-owned until copied by the driver.

## Dependencies and Integration Points
The header integrates kernel ioctl encoding, `__user` pointers, compat support under `CONFIG_COMPAT`, and HP legacy tooling. The adapter type constants map driver bus types to SCSI, FC, FC-IP, and SAS interface identifiers consumed by management applications.

## Risks and Edge Cases
Several structures contain user pointers and flexible one-element trailing arrays, so size calculations in the implementation must remain exact. ABI revisions exist because of alignment and PCI-info layout changes; changing fields would break older tools. Compat structures are only available in kernel builds with `CONFIG_COMPAT`. Raw command fields expose multiple independent sizes and pointers that require strict validation by `mptctl.c`.

## Test Signals
Tests should verify ioctl numbers remain stable, structure sizes match expected 32-bit and 64-bit ABIs, all `MPTIOCINFO` revisions are accepted, compat pointer translation works, and variable-length commands reject undersized `maxDataSize` values.
