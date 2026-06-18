# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_vf_device.c

## Purpose
This file implements CN23XX Virtual Function hardware setup for LiquidIO. It configures VF-visible queues, mailbox communication with the PF, PF/VF handshake, MSI-X interrupt decoding, queue enable/disable, and VF function-table registration.

## Important APIs, Types, And Functions
External APIs are `cn23xx_setup_octeon_vf_device()`, `cn23xx_octeon_pfvf_handshake()`, `cn23xx_vf_ask_pf_to_do_flr()`, and `cn23xx_vf_get_oq_ticks()`. Internal helpers reset queues, configure global input/output registers, setup IQ/OQ descriptors, setup/free the single VF mailbox, process mailbox work, handle MSI-X interrupts, update IQ read indices, and enable/disable output/input/mailbox interrupts.

## Control Flow
`cn23xx_setup_octeon_vf_device()` maps BAR0, reads PF number, VF number, and `rings_per_vf` from VF input-control register fields, clamps ring count against requested queues and CPU count, obtains CN23XX config, and installs VF function pointers into `oct->fn_list`. Device register setup resets VF queues and programs endian/order/snoop controls and thresholds. Mailbox setup builds one mailbox using VF read/write signal registers and writes the PF/VF signature. The handshake sends `OCTEON_VF_ACTIVE` with driver version, waits for the PF response, copies `pfvf_hsword`, pushes the PF-provided `pkind` into each IQ, and rejects major-version mismatches. MSI-X handling reads the DROQ packet-sent register, returns PO/PI bits, dispatches mailbox interrupt work for queue 0, and defers count clearing to read-index updates.

## State And Persistence
State lives in the shared `octeon_device`: VF number, PF number, `sriov_info.rings_per_vf`, `pfvf_hsword`, IQ/DROQ register pointers, mailbox object, and function table. Hardware queue state lives in VF BAR0 CSRs. No filesystem persistence exists.

## Dependencies And Integration Points
The file depends on LiquidIO core queue/mailbox/config abstractions, CN23XX VF register definitions, PCI BAR mapping helpers, MSI-X vector handling, delayed work, and PF cooperation through the mailbox protocol.

## Risks
The handshake waits in one-jiffy sleeps up to a large fixed count; PF absence or mailbox failure delays probe. `atomic_set(&status, 0)` happens after `octeon_mbox_write()`, so a very fast callback could be overwritten; this ordering deserves review. Input-interrupt enable/disable loops use `oct->num_oqs` while touching IQ registers, which is safe only if IQ/OQ counts match. Queue reset shares a single loop counter across queues. The VF relies on PF-programmed read-only fields for ring count and identity.

## Test Signals
Test VF probe with PF configured for different rings-per-VF values, CPU-count clamping, PF/VF handshake success and version mismatch, mailbox interrupt delivery, FLR request mailbox command, MSI-X PO/PI/mailbox bits, queue reset under traffic, and PF removal while VF waits for handshake.
