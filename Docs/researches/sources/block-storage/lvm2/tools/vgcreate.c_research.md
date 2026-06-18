# File Research: sources/block-storage/lvm2/tools/vgcreate.c

Purpose: implements `vgcreate`, creating a new volume group from supplied PV devices with metadata, locking, devices-file, persistent reservation, and profile initialization.

Read coverage: complete file read, 218 lines.

Key responsibilities:
- Parses VG name, PV creation parameters, and VG creation parameters from command-line arguments.
- Preserves existing PVs rather than creating over existing PV metadata and checks consistent block sizes.
- Takes global and lockd creation locks, clears hints, locks the future VG name, and label-scans before PV creation to ensure the VG name does not already exist.
- Enables devices-file creation/editing and runs `pvcreate_each_device()`.
- Creates the VG object, applies default/profile metadata, extent size, max LV/PV, allocation policy, system ID, metadata copies, and persistent reservation flags.
- Adds PVs to the VG, applies tags from grouped `--addtag`, writes and commits metadata.
- Initializes lockd metadata in a second write for shared VGs and starts the lockspace, optionally waiting for readiness.
- Starts persistent reservation for shared VGs when requested.

Dependencies:
- Uses PV create and VG create parameter helpers, device persist helpers, lvmcache, locking/lvmlockd, VG metadata setters, tag mutation, devices file handling, and lockspace startup.

Risks and edge cases:
- VG name existence is checked only after taking the new VG lock and scanning labels, before any PVs are modified.
- Shared VG creation is two-stage: initial local metadata, then lockd initialization with lock args.
- Failure after lockd initialization attempts to remove PVs and VG metadata directly before returning failure.
