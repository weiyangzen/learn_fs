# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp6000_pcie.c

Purpose: Implements the NFP6000/NFP3800 PCIe transport for the generic `nfp_cpp` bus. It multiplexes PCIe BAR apertures into CPP targets, maps reserved CSR/SRAM/explicit regions, and supplies `struct nfp_cpp_operations` callbacks used by `nfp_cppcore.c`.

Important APIs/types/functions: `struct nfp_bar` tracks BAR config, base, aperture mask, refcount, iomem, and PCI resource. `struct nfp6000_pcie` owns PCI device state, BAR lock/waitqueue, reserved mappings, and explicit transaction slot state. `compute_bar()`, `matching_bar()`, `find_unused_bar_noblock()`, and `nfp_alloc_bar()` are the allocation core. `enable_bars()` configures reserved BAR0 slices for MSI-X SRAM, XPB, and explicit access. `nfp6000_area_*()` implements normal CPP area mapping/read/write. `nfp6000_explicit_*()` implements explicit CPP transactions. `nfp_cpp_from_nfp6000_pcie()` is the exported construction path.

Control flow: probe allocates `nfp6000_pcie`, validates the PCI interface encoded in the DSN, calls `enable_bars()`, then creates a generic CPP handle with `nfp_cpp_from_operations()`. Area acquisition first tries an existing compatible BAR, then finds or waits for a free BAR, writes the BAR CSR, computes the physical/iomem offset, and increments private and BAR refcounts. Aligned reads/writes use raw 32/64-bit MMIO; unaligned requests fall back to explicit transactions. Explicit access picks a free group/slot, writes three explicit BAR CSRs, kicks the transaction by reading the mapped address, and exchanges data through the reserved SRAM data window.

State and persistence: State is kernel-resident only: BAR config cache, atomic BAR refcounts, per-area refcounts, wait queues, and explicit slot bitmaps. Hardware-visible state includes PCIe BAR CSR programming and explicit command CSRs. No filesystem persistence is used.

Dependencies/integration: Depends on Linux PCI/MMIO APIs, `nfp_cpp.h` operation contracts, `nfp_dev_info` offsets, and target width decoding from `nfp_target_pushpull()`. It is the low-level backend for all CPP users including resources, NSP, firmware tables, and NIC DCB symbol mapping.

Risks: BAR allocation is concurrency-sensitive; missed refcount drops can starve later CPP users. Incorrect width/action decoding can cause invalid or partial device transactions. Explicit access relies on bounded slot availability and correct signal/data reference calculation. The source snapshot contains duplicated-looking lines in comments/near surrounding copied code, so build validation is an important signal.

Test signals: PCI probe should log NFP card probe, link status, reserved BAR layout, and model information. Exercise `nfp_cpp_readl/writeq`, unaligned explicit reads/writes, resource acquisition, NSP commands, and driver unload to confirm iounmap/refcount cleanup without dangling area warnings.
