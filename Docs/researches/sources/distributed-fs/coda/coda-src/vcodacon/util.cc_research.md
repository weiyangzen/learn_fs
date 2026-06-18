# sources/distributed-fs/coda/coda-src/vcodacon/util.cc

## Purpose
This file implements utility callbacks for the `vcodacon` GUI: initialization, realm discovery, Coda login/logout commands, token display, and realm path validation.

## Important APIs, Types, and Functions
`XferLabel[3]` mirrors transfer labels for GUI progress slots. Realm state is held in `realmlist`, `nlist`, and `nrealm`. `lookup_realm()` searches the list, `add_realm()` grows it, and `update_realmlist()` scans `/coda` for non-hidden realm names while rejecting `NOT_REALLY_CODA`. `do_clog()` runs `clog -pipe`, writes the password to stdin, and hides the login window. `do_cunlog()` runs `cunlog @realm`. `menu_clog()`, `menu_cunlog()`, and `menu_ctokens()` populate and show FLTK dialogs. `do_findRealm()` stats `/coda/<realm>`. `MainInit()` hides progress widgets and seeds the realm list from `venus.conf`.

## Control Flow
Menu callbacks refresh realm choices from `/coda`, populate FLTK widgets, and show dialogs. Login/logout callbacks validate GUI selections, construct command lines, invoke subprocesses through `popen`, report failures via `fl_alert`, and clear sensitive UI state on success.

## State and Persistence Behavior
The file only stores process-local GUI state and a heap-allocated realm list. Persistent Coda authentication tokens are changed indirectly by external `clog` and `cunlog` commands.

## Dependencies and Integration Points
It depends on generated GUI globals from `vcodacon.h`, FLTK alerts/widgets, `/coda`, `venus.conf` via `codaconf`, and command-line tools `clog`, `cunlog`, and `ctokens`.

## Risks and Test Signals
Risks include command injection through usernames or realm names, leaked realm strings, early return from `update_realmlist()` without `closedir`, fixed-size command buffers, and password handling through a pipe. Tests should cover empty user/realm selections, missing `/coda`, seeded `venus.conf` realms, malformed realm names, failed subprocesses, and token list refresh.
