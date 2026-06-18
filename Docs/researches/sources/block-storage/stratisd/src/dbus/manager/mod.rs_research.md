# File Research: sources/block-storage/stratisd/src/dbus/manager/mod.rs

Purpose: Central manager module for Stratis D-Bus object-path bookkeeping and manager/report interface registration.

Key structures:
- `Manager` stores bidirectional maps for pool, filesystem, and blockdev object paths to UUIDs.
- Provides add/get/remove helpers for each object category.
- Add helpers permit exact duplicate path/UUID pairs, warn for some path conflicts, and error for conflicting UUID-to-path mappings.

Registration behavior:
- Imports and reexports Manager r0 through r9.
- Imports and reexports Report r0 through r9.
- `register_manager` registers every manager and report revision at `STRATIS_BASE_PATH`.
- Also registers `zbus::fdo::ObjectManager` at the base path.

Important role:
- This file is the shared registry used by manager, pool, filesystem, blockdev, and udev D-Bus code to translate engine UUIDs into stable exported object paths.
