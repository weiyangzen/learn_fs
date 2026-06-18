# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_introspect.py

## Role

Stores embedded D-Bus introspection XML used to generate the client classes in `_actions/_data.py`.

## Interfaces Covered

The `SPECS` dictionary includes XML for:

- `org.freedesktop.DBus.ObjectManager`
- `org.storage.stratis3.Manager.r9`
- `org.storage.stratis3.Report.r9`
- `org.storage.stratis3.blockdev.r9`
- `org.storage.stratis3.filesystem.r9`
- `org.storage.stratis3.pool.r9`

## API Surface Represented

The XML includes manager methods such as pool creation/destruction/start/stop, key handling, reports, and refresh; report retrieval; blockdev properties; filesystem properties and operations; and pool methods/properties for devices, cache, filesystems, encryption, metadata, rename, bind/rebind/unbind, grow, and reencrypt.

## Dependencies

No imports. This is pure data consumed by XML parsing and code generation.

## Notable Risk Areas

This file is the local contract between `stratis-cli` and `stratisd`. If the XML diverges from daemon behavior, generated clients can fail at runtime or `_error_reporting.py` may report an interface mismatch.
