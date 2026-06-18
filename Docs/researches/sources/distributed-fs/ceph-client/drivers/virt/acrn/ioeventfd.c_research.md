# sources/distributed-fs/ceph-client/drivers/virt/acrn/ioeventfd.c

Purpose: ACRN HSM ioeventfd support. It lets userspace associate eventfd objects with expected User VM MMIO or PIO writes, allowing fast notification paths for emulated devices such as vhost/virtio.

Important APIs, types, and functions: internal `struct hsm_ioeventfd` stores list linkage, eventfd context, address, data match, length, type, and wildcard flag. Public internal APIs are `acrn_ioeventfd_init`, `acrn_ioeventfd_config`, and `acrn_ioeventfd_deinit`. Helpers include `ioreq_type_from_flags`, `acrn_ioeventfd_shutdown`, `hsm_ioeventfd_is_conflict`, `acrn_ioeventfd_assign`, `acrn_ioeventfd_deassign`, `hsm_ioeventfd_match`, and `acrn_ioeventfd_handler`.

Control flow: init creates a non-default ioreq client named `ioeventfd-<vmid>` with `acrn_ioeventfd_handler` and initializes the VM list/mutex. Config either assigns or deassigns based on `ACRN_IOEVENTFD_FLAG_DEASSIGN`. Assign validates range overflow and allowed widths 1/2/4/8, obtains an eventfd context from the userspace fd, allocates state, sets PIO or MMIO type, determines wildcard versus data-match behavior, rejects conflicts under the VM mutex, registers the I/O range with the ioreq client, and appends to the list. Handler ignores reads by returning zero data, matches writes by type/address/length/data, and signals the eventfd. Deinit destroys the ioreq client and shuts down all eventfds.

State and persistence: per-VM linked list of ioeventfd registrations protected by `ioeventfds_lock`; each entry holds an eventfd reference until deassign or deinit. Registrations last for the VM lifetime or until explicit deassign.

Dependencies and integration points: depends on Linux eventfd, ACRN ioreq clients/ranges, UAPI `struct acrn_ioeventfd`, and VM state in `acrn_drv.h`. Integrated through `ACRN_IOCTL_IOEVENTFD` in `hsm.c`.

Risks: conflict detection is keyed by eventfd, address, type, and data/wildcard overlap; different eventfds can register overlapping ranges, so dispatch semantics depend on ioreq range routing. Deassign matches only by eventfd, not by address/data, so one fd registration is removed per call. Handler requires exact base address match and `p->length >= len`, not containment of sub-offsets. Reads are deliberately ignored and return zero.

Test signals: ioctl assign/deassign for MMIO and PIO, invalid widths, overflow address+len, eventfd fd errors, duplicate/conflicting registrations, wildcard and data-match writes, ignored reads, concurrent config and ioreq handling, VM deinit cleanup and eventfd reference release.
