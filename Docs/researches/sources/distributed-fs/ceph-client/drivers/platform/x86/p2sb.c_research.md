# sources/distributed-fs/ceph-client/drivers/platform/x86/p2sb.c

Purpose: This file provides exported support for retrieving the BAR0 memory resource of Intel Primary-to-Sideband (P2SB) bridge functions, including devices hidden by firmware. It lets other drivers call `p2sb_bar()` without temporarily exposing the hidden PCI device during later sysfs rescans.

Important APIs, types, and functions: `p2sb_bar()` is the exported GPL API. `p2sb_get_devfn()` chooses the default P2SB devfn, with Goldmont/Goldmont Plus overrides. `struct p2sb_res_cache` stores a bus id and copied resource per PCI function. `p2sb_cache_resources()` runs at `fs_initcall_sync`, hides/unhides the device under `pci_lock_rescan_remove()`, and caches BAR0. `p2sb_read_from_cache()` and `p2sb_read_from_dev()` serve callers depending on whether BIOS hid the bridge.

Control flow: Early init finds bus 0/domain 0, verifies the P2SB devfn is not an unrelated device by checking class code, records whether BIOS set `P2SBC_HIDE`, and if hidden clears the hide bit, scans the P2SB function, copies BAR0, optionally scans Goldmont SPI function, removes the temporary devices, and hides P2SB again. Later `p2sb_bar()` resolves a bus and devfn, then returns either cached resource data or live PCI resource data.

State and persistence: State is global and static: `p2sb_resources[]`, `p2sb_hidden_by_bios`, and a cached bus pointer in `p2sb_get_bus()`. It persists for the kernel lifetime and is not revalidated after PCI topology changes. Copied resources intentionally avoid pointer fields because scanned devices are removed immediately.

Dependencies and integration points: The code integrates with PCI core scanning/removal locks, x86 CPU matching, Intel family identifiers, and `linux/platform_data/x86/p2sb.h`. Downstream users include sideband, GPIO, SPI, and PMC-related drivers that need the P2SB BAR.

Risks and edge cases: The cache assumes PCI bus identity remains valid and only covers eight functions. Failure to cache hidden resources early leaves later callers without a safe way to expose P2SB. The init code avoids touching a different device at the same devfn by class check, but firmware/platform quirks can still make BAR validity fragile. The comment notes a duplicated PCI-function-count constant.

Test signals: Boot logs and callers of `p2sb_bar()` should be tested on hidden and visible P2SB systems, especially Goldmont where SPI is also cached. PCI rescan/sysfs stress should verify no deadlock and no transient exposed P2SB device remains. Unit-style checks can validate `p2sb_valid_resource()` behavior for unset resources.
