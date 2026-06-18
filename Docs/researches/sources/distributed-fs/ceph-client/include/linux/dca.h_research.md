# sources/distributed-fs/ceph-client/include/linux/dca.h

Purpose: Declares the Direct Cache Access provider/requester API used by PCI devices and platforms that support CPU-cache-targeted DMA hints.

Important APIs, types, and functions: Defines notifier events `DCA_PROVIDER_ADD` and `DCA_PROVIDER_REMOVE`, `struct dca_provider`, `struct dca_domain`, and `struct dca_ops` callbacks for requester add/remove, tag lookup, and device-management checks. Provider APIs allocate, free, register, unregister, and expose private storage via `dca_priv()`. Requester APIs add/remove devices and get CPU tags through `dca_get_tag()`/`dca3_get_tag()`. Internal sysfs helpers create provider/requester attributes.

Control flow: A hardware provider registers with DCA ops and a device, requesters attach if they share a compatible domain/root complex, and data paths query CPU tags for DMA steering. Notifiers announce provider availability changes to interested subsystems.

State and persistence: Runtime state consists of provider/domain lists, provider IDs, requester slots, and sysfs entries. There is no persistent state.

Dependencies and integration points: Depends on PCI bus topology and generic device/sysfs infrastructure. It integrates with DCA-capable NIC/storage drivers and provider drivers that implement hardware tag programming.

Risks and test signals: Risks include matching requesters to the wrong PCI domain, stale sysfs/requester entries after provider removal, CPU hotplug tag issues, and provider private-data sizing mistakes. Test provider add/remove, requester lifecycle, tag lookup across CPUs, sysfs visibility, and builds with DCA consumers.
