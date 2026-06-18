# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/hwrpb.h

This header defines the Alpha Hardware Restart Parameter Block contract. It declares the initial HWRPB address, architected CPU and system type constants, and structures for PCB, per-CPU data, procedure descriptors, console callback routine block mappings, memory descriptors/clusters, dynamic system recognition data, and the top-level `hwrpb_struct`.

The important API is global `hwrpb` plus `hwrpb_update_checksum`, which sums all quadwords before `chksum` and writes the checksum. HWRPB fields provide page size, physical address bits, max ASN, system identity, clock frequencies, VPTB, processor tables, console terminal/callback offsets, memory descriptor offsets, restart callbacks, and FRU/DSR pointers.

State is firmware-owned boot/runtime configuration shared with the kernel and bootloaders. Integration is everywhere in Alpha early boot, PAL setup, console callbacks, memory discovery, CPU discovery, and platform selection. Risks are binary layout fidelity, flexible-array offset arithmetic, checksum correctness, and assuming `INIT_HWRPB` contents before validation. Tests are boot on SRM/QEMU, HWRPB parsing, checksum update coverage, and platform detection.
