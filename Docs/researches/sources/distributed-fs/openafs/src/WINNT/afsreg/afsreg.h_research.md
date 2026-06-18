# sources/distributed-fs/openafs/src/WINNT/afsreg/afsreg.h

## Purpose
Defines OpenAFS Windows registry key/value constants and declares the extended registry helper API implemented by `afsreg.c`.

## Important APIs, Types, And Functions
The header names service identifiers (`TransarcAFSServer`, `TransarcAFSDaemon`), software keys under `Software\TransarcCorporation`, client OpenAFS keys, event-log keys, TCP/IP interface keys, server Afstab keys, client service parameter/provider keys, and network-provider order values. It defines `regentry_t` with `REGENTRY_KEY` and `REGENTRY_VALUE`, plus prototypes for `RegOpenKeyAlt`, `RegQueryValueAlt`, `RegEnumKeyAlt`, `RegDeleteKeyAlt`, `RegDeleteEntryAlt`, `RegDupKeyAlt`, and `IsWow64`.

## Control Flow
Consumers combine these constants with the helper functions to open, read, write, delete, or duplicate OpenAFS-related registry state. The constants encode both canonical full paths and subkey paths so callers can start at `AFSREG_NULL_KEY` or an already-open parent.

## State And Persistence
The file itself has no runtime state, but it defines the persistent registry schema for OpenAFS server/client install metadata, service configuration, event-log source registration, client cell and CellServDB location, server vice partition table entries, TCP/IP interface inspection, and network provider ordering.

## Dependencies And Integration Points
It requires Win32 `HKEY`/`TEXT` types from `windows.h` in consumers. It is shared by registry helpers, installers/configuration tools, server partition table code, and system interface discovery.

## Risks And Test Signals
Changing any string can break installers, services, or backwards compatibility with existing registry installations. Header compile coverage and install/configuration smoke tests that verify expected key names are the relevant signals.
