# File Research: sources/block-storage/parted/libparted/fs/amiga/a-interface.c

Registration glue for Amiga filesystem probes. `ped_file_system_amiga_init()` registers all Amiga-related `PedFileSystemType` instances, and `ped_file_system_amiga_done()` unregisters them in the same family list.

Registered types include AFFS variants `affs0` through `affs7`, muFS variants `amufs`, `amufs0` through `amufs5`, `asfs`, and PFS/APFS-style `apfs1` and `apfs2`. The file has no probe logic; it imports the type globals from the individual implementation files.

The order matters because libparted’s filesystem registry is a stack-like linked list. Registration prepends each type, so effective probe order is reverse registration order unless later modules alter the registry.
