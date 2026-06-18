# sources/distributed-fs/openafs/src/butc/butc_xbsa.h

## Purpose
`butc_xbsa.h` defines the Tape Coordinator's XBSA configuration, server-type constants, transaction state, public wrapper prototypes, and global XBSA command-line/configuration variables.

## Important APIs, Types, And Functions
It defines server types and masks (`XBSA_SERVER_TYPE_NONE`, `UNKNOWN`, `ADSM`, `MASK`), conditional `CONF_XBSA`, server flags (`XBSA_SERVER_FLAG_MULTIPLE`, `NONE`), buffer limits (`XBSAMINBUFFER`, `XBSADFLTBUFFER`, `XBSAMAXBUFFER`), ADSM version thresholds for multiple-server support, and XBSA technical-standard version constants. `struct butx_transactionInfo` stores API version, handle, server type, max/active object counts, server name, security token, owner, and current object. The header declares all `xbsa_*` wrapper functions used by coordinator dump/restore code.

## Control Flow
The header itself has no runtime flow, but its macros control whether XBSA code is active and how server type/flag bitfields are read and written. Under `NEW_XBSA` it includes the local `afsxbsa.h`; otherwise it includes the platform `<xbsa.h>`.

## State And Persistence
It declares global XBSA settings with `XBSA_EXT`: `xbsaType`, and when `xbsa` is enabled, `butxInfo`, `dumpRestAuthnLevel`, `xbsaObjectOwner`, `appObjectOwner`, `adsmServerName`, `xbsaSecToken`, and `xbsalGName`. These globals represent coordinator configuration and session state; persistence is in the remote XBSA server accessed through the wrappers.

## Dependencies And Integration Points
The header bridges coordinator code, the BUTX error/API layer, the local XBSA adapter, and external XBSA headers. It is included by both the wrapper implementation and coordinator modules that need to know whether XBSA is configured.

## Risks And Test Signals
The main risks are conditional compilation skew and ABI mismatches between local and external XBSA headers. The handle type changes under `NEW_XBSA`, so tests must cover both configurations. Buffer limits are constrained by BSA's 16-bit `DataBlock` lengths, so boundary tests should cover 0, `XBSAMINBUFFER`, `XBSADFLTBUFFER`, `XBSAMAXBUFFER`, and oversized buffers.
