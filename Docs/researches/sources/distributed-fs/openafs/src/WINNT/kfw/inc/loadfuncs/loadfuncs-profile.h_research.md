# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-profile.h

## Purpose

This header declares dynamic bindings for the Kerberos profile library (`xpprof32.dll` or `xpprof64.dll`). It lets OpenAFS/KFW code read, enumerate, update, and flush Kerberos profile configuration without a static dependency.

## Important APIs, Types, and Functions

- `PROFILE_DLL` selects `xpprof64.dll` on `_WIN64`, otherwise `xpprof32.dll`.
- Initialization and lifecycle: `profile_init`, `profile_init_path`, `profile_flush`, `profile_abandon`, and `profile_release`.
- Reads and enumeration: `profile_get_values`, `profile_get_string`, `profile_get_integer`, `profile_get_relation_names`, `profile_get_subsection_names`, `profile_iterator_create`, `profile_iterator`, and `profile_iterator_free`.
- Memory cleanup: `profile_free_list` and `profile_release_string`.
- Mutation APIs: `profile_update_relation`, `profile_clear_relation`, `profile_rename_section`, and `profile_add_relation`.

## Control Flow

Callers load the DLL, initialize a `profile_t` from file specs or a path list, perform lookup/iteration/mutation calls, then either flush changes or abandon/release the profile. Iterators are explicit objects that must be freed after traversal.

## State and Persistence Behavior

The external profile library owns parsed profile state and writes modifications to profile files when flushed. `profile_abandon` discards a profile handle without committing changes, while `profile_release` and `profile_flush` determine handle lifetime and persistence semantics according to the profile library. Returned lists and strings require library-specific release functions.

## Dependencies and Integration Points

Depends on `loadfuncs.h` and `<profile.h>`. It integrates with Kerberos profile configuration, likely including realm, domain, KDC, and library default settings consumed by KRB5/Leash paths.

## Risks

- Mutating profile relations can change global Kerberos behavior for the user or machine.
- Callers must pair allocated return values with `profile_free_list` or `profile_release_string`.
- Profile path parsing and write permissions vary by Windows environment.
- Partial dynamic loads can leave mutation APIs unavailable even if read APIs load.

## Test Signals

Use temporary profile files to test initialization, string/integer lookup, relation enumeration, add/update/clear/rename, flush, and abandon behavior. Loader tests should verify architecture-specific DLL naming and missing-DLL failure behavior.
