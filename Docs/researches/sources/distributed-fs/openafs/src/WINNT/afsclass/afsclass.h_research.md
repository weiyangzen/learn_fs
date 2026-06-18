# sources/distributed-fs/openafs/src/WINNT/afsclass/afsclass.h

## Purpose
Public umbrella header for the Windows `afsclass` object model. It establishes common constants and forward declarations, includes the class-specific headers, and declares library-level initialization, locking, refresh-domain, time, allocation, and address helpers.

## Important APIs and Types
Constants include `cchNAME`, ghost-status bit masks, and refresh-domain flags (`AFSCLASS_WANT_VOLUMES`, `AFSCLASS_WANT_USERS`). `ACCOUNTACCESS` abstracts PTS permission visibility. The header aliases `HENUM` to `LPENUMERATION` from the hashlist library and declares `VOLUMEID`, notification, cell, server, service, aggregate, fileset, user, group, ident, and ident-list classes.

It includes `c_debug.h`, `c_notify.h`, `c_ident.h`, `c_identlist.h`, `c_cell.h`, `c_svr.h`, `c_svc.h`, `c_agg.h`, `c_set.h`, `c_usr.h`, `c_grp.h`, and `afsclassfn.h`. Declared utility functions are `AfsClass_Initialize`, `AfsClass_SpecifyRefreshDomain`, `AfsClass_Enter`, `AfsClass_Leave`, `AfsClass_GetEnterCount`, `AfsClass_RequestLongServerNames`, Unix/system time conversion, `AfsClass_ReallocFunction`, `AfsClass_SkipRefresh`, and address conversions.

## State, Dependencies, and Integration
This header is the main entry point for applications using the AFS admin class library. It depends on `WINNT/afsapplib.h` and the full afsclass object hierarchy. The explicit enter/leave API exposes a global class lock used heavily by action wrappers in `afsclassfn.cpp`.

## Risks and Test Signals
The umbrella inclusion pattern can hide heavy dependencies and compile-time coupling. `cchNAME` fixed buffers are common across implementations, so truncation/overflow behavior is a key integration risk. Tests should validate initialization, lock recursion/count reporting, refresh-domain flags, time conversion round trips, address conversion, and inclusion order with both C and C++ Windows build settings.
