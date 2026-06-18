# sources/distributed-fs/openafs/src/afs/afs_consts.h

Purpose: Provides small shared cache-manager constants for host-list and pioctl sizing.

Important APIs and definitions: `AFS_MAXHOSTS` is the maximum hosts per volume, `AFS_OMAXHOSTS` preserves the old eight-host compatibility value, `AFS_MAXCELLHOSTS` is the maximum VLDB servers per cell, and `AFS_PIOCTL_MAXSIZE` caps returned pioctl data.

Control flow: No runtime logic. These constants constrain array sizes and loops throughout volume, cell, connection, analyze, and pioctl code.

State and persistence: No state or persistence.

Dependencies and integration points: Used by cell host arrays, volume server host/status arrays, request skip/error arrays, callback/cell RPC reporting, and pioctl buffer sizing.

Risks: Changing these values is ABI- and structure-sensitive. Arrays in persisted or RPC-facing structures may still assume old limits, especially where `AFS_OMAXHOSTS`, `AFS_MAXHOSTS`, and `AFS_MAXCELLHOSTS` differ.

Test signals: Compile-time structure-size checks, loops over max host counts, compatibility with old VLDB/volume entries, pioctl maximum return tests, and boundary cases for exactly max hosts/cell hosts.
