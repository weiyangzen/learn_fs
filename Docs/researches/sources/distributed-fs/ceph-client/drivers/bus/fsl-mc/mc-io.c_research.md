# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/mc-io.c

Purpose: manages MC portal I/O objects. It maps portal MMIO, associates portals with DPMCP objects, allocates portals from MC bus resource pools, and releases them back to the pool.

Important APIs: `fsl_create_mc_io()` creates an `fsl_mc_io` with either mutex or raw spinlock serialization depending on `FSL_MC_IO_ATOMIC_CONTEXT_PORTAL`; `fsl_destroy_mc_io()` unmaps and releases the portal; `fsl_mc_portal_allocate()` allocates a DPMCP resource and wraps its MMIO region; `fsl_mc_portal_free()` destroys the wrapper and returns the resource. Internal helpers open/close DPMCPs and bind `dpmcp_dev->mc_io`.

Control flow: creation allocates managed memory, requests the portal memory region, maps it, initializes locking, and optionally opens a DPMCP. Portal allocation resolves the owning DPRC, allocates a DPMCP resource, validates its minimum API version, creates an MC I/O object on the DPMCP region, and adds a device link from consumer to DPMCP except when the DPRC consumes its own portal for UAPI.

State and persistence: state is in `struct fsl_mc_io`, DPMCP device handle fields, resource ownership, and optional device links. Nothing persists outside kernel runtime; the firmware DPMCP open handle is closed on destruction.

Dependencies and integration: depends on FSL MC resource pools, DPMCP open/close commands, devm memory-region/ioremap helpers, device links, and public MC command sending. It is used by root bus probe, UAPI open, MC object drivers, and allocator users.

Risks: portal ownership must be exclusive; double assignment is rejected by checking both `mc_io->dpmcp_dev` and `dpmcp_dev->mc_io`. DPMCP version mismatches fail allocation. Early returns in `fsl_mc_portal_free()` can leak a malformed resource state if invariants are already broken. Test signals include root portal creation, dynamic portal allocation/free, DPMCP open/close failures, device-link creation, atomic-context portal use, and resource pool accounting.
