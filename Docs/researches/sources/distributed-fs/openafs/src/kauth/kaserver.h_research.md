# sources/distributed-fs/openafs/src/kauth/kaserver.h

## Purpose
Defines the on-disk KA database layout, key/entry structures, statistics macros, offset helpers, and shared kaserver globals/prototypes.

## Important APIs, Types, And Functions
Defines `KADBVERSION`, `HASHSIZE`, `NULLO`, `struct kaheader`, `ENTRYSIZE`, `KA_NPWSUMS`, `struct kaentry`, `struct kaOldKey`, `struct kaOldKeys`, `NOLDKEYS`, password-control byte indexes, `COUNT_REQ`, `COUNT_ABO`, `DOFFSET`, and `IOFFSET`. It declares globals such as `cheader`, `dynamic_statistics`, `myHost`, and `krb4_cross`, plus auxiliary DB and `es_Report` functions.

## Control Flow
No runtime flow lives in the header. The macros are expanded inside request handlers and database helpers to update statistics and compute disk offsets.

## State And Persistence
This file is the authoritative description of KA persistent database records. Fields are documented as network byte order; record size is fixed at 200 bytes, and the header embeds the name hash table and version sentinels.

## Dependencies And Integration Points
It is included by `kadatabase.c`, `kaprocs.c`, `kaserver.c`, `ka_util.c`, and `kaauxdb.c`. It must remain compatible with Ubik storage, generated kauth types, and old database files.

## Risks And Test Signals
Risks include ABI/layout drift, `ENTRYSIZE` padding assumptions, endian mistakes, and changing `HASHSIZE` or fields without migration. Test signals include `sizeof(struct kaentry) == sizeof(struct kaOldKeys)`, database version checks, dump/restore compatibility, old-key rollover, and cross-version server startup against test databases.
