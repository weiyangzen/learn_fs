# sources/distributed-fs/openafs/src/kauth/kalocalcell.c

## Purpose
Provides kauth cell/realm helper routines isolated from other kauth modules so consumers can use afsconf without awkward linker dependencies.

## Important APIs, Types, And Functions
Exports `ka_CellConfig`, `ka_LocalCell`, `ka_ExpandCell`, and `ka_CellToRealm`. Static state consists of an `afsconf_dir *conf` and cached `cell_name`.

## Control Flow
`ka_CellConfig` closes any prior config directory, opens the supplied directory, and caches the local cell. `ka_LocalCell` lazily opens the client etc directory and fetches the local cell if not already configured. `ka_ExpandCell` resolves an empty cell to the local cell or lowercases and looks up a named cell in CellServDB, returning the canonical cell and whether it is local. `ka_CellToRealm` expands the cell and uppercases the result as the Kerberos realm.

## State And Persistence
Runtime state is the cached config handle and local cell name protected by the global pthread lock macros. The code reads CellServDB-style configuration but does not write it.

## Dependencies And Integration Points
It depends on afsconf, global pthread locking, Rx/XDR includes required by kauth headers, and string case helpers. It is used by clients, token functions, `klog`, `kpasswd`, and server initialization.

## Risks And Test Signals
Risks include global mutable config state shared by all callers, `strcpy` into caller buffers whose sizes are assumed by convention, and error paths that leave `conf` as NULL. Test signals include local-cell discovery, alternate config directory selection, canonical cell expansion, unknown-cell failure, realm uppercase conversion, and concurrent callers.
