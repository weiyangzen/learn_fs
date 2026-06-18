# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/sdsi.c

## Purpose

This file implements the Intel On Demand / Software Defined Silicon auxiliary driver. It maps SDSi mailbox/register regions discovered by Intel VSEC, exposes provisioning and certificate/register binary sysfs files, and performs in-band mailbox transactions using required 64-bit MMIO accesses.

## Important APIs, Types, And Functions

Key types are `struct sdsi_priv`, `struct sdsi_mbox_info`, and `struct disc_table`. Mailbox helpers include `sdsi_mbox_acquire()`, `sdsi_mbox_cmd_write()`, `sdsi_mbox_cmd_read()`, `sdsi_mbox_poll()`, and `sdsi_complete_transaction()`. User-facing sysfs handlers are `provision_akc_write()`, `provision_cap_write()`, `state_certificate_read()`, `meter_certificate_read()`, `meter_current_read()`, `registers_read()`, and `guid_show()`. Probe uses `sdsi_get_layout()` and `sdsi_map_mbox_registers()`.

## Control Flow

Probe binds to `intel_vsec.sdsi`, reads the discovery table, selects layout based on SDSi GUID v1 or v2, maps the SDSi region from either local discovery-relative addressing or PCI BAR addressing, and reads feature bits. Sysfs visibility always exposes `registers`; provisioning and certificate files require the SDSi feature bit, and metering files additionally require the metering bit. Provision writes reject nonzero offsets, check in-band lock, build a qword-aligned payload with the command in the final qword, acquire the mailbox, write the payload, and poll completion. Certificate reads acquire the mailbox, issue a read command, collect up to four 1 KiB packets, and copy the result to sysfs.

## State And Persistence

`sdsi_priv` holds the mailbox mutex, mapped control/mailbox/register pointers, selected layout sizes, GUID, and feature bits. There is no persistent software storage. Provisioning commands can have persistent platform/license effects in hardware or firmware; the driver only transports the payload.

## Dependencies And Integration Points

The driver integrates with Intel VSEC auxiliary devices, PCI resources, sysfs binary attributes, admin-only bin attributes, `readq_poll_timeout()`, and strict 64-bit MMIO copy helpers. It relies on firmware mailbox ownership and status protocol.

## Risks

Provisioning is security-sensitive and irreversible on some platforms, so visibility gating and `BIN_ATTR_ADMIN_RO`/write-only permissions are important. `sdsi_mbox_acquire()` can take several retries after recent transactions. Packet-size, EOM, and total-message validation protect against firmware protocol errors, but malformed firmware responses still result in partial warnings or `-EPROTO`. A typo in `maibox_size` is harmless because the field is unused. Layout and access-type decoding must match VSEC discovery exactly.

## Test Signals

Signals include correct sysfs file visibility from feature bits, GUID v1/v2 layout mapping, register reads clipped to actual size, provisioning rejects nonzero offsets and locked mailboxes, mailbox timeout/ownership/status paths, multi-packet certificate reads, and admin permission behavior.
