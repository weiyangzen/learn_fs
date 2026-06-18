# sources/distributed-fs/openafs/src/auth/test/testcellconf.c

## Purpose
Interactive test utility for cell configuration APIs: local cell discovery, cell database enumeration, service lookup, extended clone information, and reload behavior.

## Important APIs, Types, and Functions
Uses `afsconf_Open`, `afsconf_GetLocalCell`, `afsconf_CellApply`, `afsconf_GetCellInfo`, `afsconf_GetExtendedCellInfo`, `_afsconf_Touch`, and `afsconf_Close`. `PrintOneCell`, `PrintClones`, and `TestCellConfig` structure output.

## Control Flow
Command options select config directory, cell list, and reload test. Without explicit cells it prints all cells plus special service lookups. With cells it prints standard and extended info per cell. `-reload` touches the config and re-queries after a delay.

## State and Persistence
Reads configuration files from a selected directory or `AFSDIR_SERVER_ETC_DIRPATH`. `-reload` mutates configuration metadata through `_afsconf_Touch` to force reload.

## Dependencies and Integration Points
Uses the OpenAFS `cmd` parser, cellconfig library, socket initialization on Windows, and service names such as `afsprot`.

## Risks and Test Signals
This is output-driven and does not assert expected values. Some branches assume service lookups exist and then print results. Test signals are absence of crashes, correct local cell reporting, sane clone flags, and reload causing fresh cell info to be read.
