# sources/distributed-fs/coda/coda-src/norton/norton.h

Purpose: shared declaration hub for Norton modules. It exposes global debug/mapping flags and all command/utility functions implemented across setup, commands, volume, vnode, recovery, directory, and RDS files.

Integration: keeps parser command files loosely coupled by declaring overloads for volume/vnode/directory functions and recoverable-storage accessors. It includes Coda volume/vnode/index/recov/camprivate headers so consumers share exact server types.

Risks: broad header coupling means small type changes in server internals ripple into all Norton files. Several declarations, such as `undelete_volume`, are present without implementation in this subset, so command availability and link targets must stay aligned. Test signal is full Norton build/link.
